import datetime, requests, http.client, urllib.request, urllib.parse, urllib.error, json
from django.contrib import auth
from django.conf import settings
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse
from accounts.models import Message
from accounts.forms import MessageForm, LoginForm

# Create your views here.



headers = {'Ocp-Apim-Subscription-Key': settings.NS_API_KEY,}
params = urllib.parse.urlencode({})
conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
conn.request("GET", "/reisinformatie-api/api/v2/stations?%s" % params, "{body}", headers)
response = conn.getresponse()
data = [i for i in json.loads(response.read().decode('utf-8'))['payload'] if i['land'] == 'NL']
conn.close()

def home(request):
    stations = [[i['namen']['lang'], i['UICCode']] for i in data]
    station_count = Message.objects.values('station').annotate(messages=Count('station'))
    station_messages = [[i[0], i[1], j['messages']] for j in station_count for i in stations if j['station'] == i[1]]
    unreviewed_count = Message.objects.filter(reviewed=None).count()
    args = {'station_messages': station_messages, 'unreviewed_count': unreviewed_count}
    return render(request, 'index.html', args)

def stations(request):
    p = Paginator([[i['namen']['lang'], i['UICCode']] for i in data], 30)
    stations = p.get_page(request.GET.get('page'))
    unreviewed_count = Message.objects.filter(reviewed=None).count()
    args = {'stations': stations, 'unreviewed_count': unreviewed_count}
    if request.GET and int(request.GET.get('page')) > 1:
        return render(request, 'partials/stations.html', args)
    return render(request, 'stations.html', args)

def station_search(request):
    if request.method == 'GET':
        q = request.GET.get('q')
        stations = [[i['namen']['lang'], i['UICCode']] for i in data if q.lower() in i['namen']['lang'].lower()]
        args = {'stations': stations}
        return render(request, 'partials/station_search.html', args)

def station(request, id):
    station = [i for i in data if i['UICCode'] == id]
    station_name = station[0]['namen']['lang']
    messages = Message.objects.filter(station=station[0]['UICCode'], approved=True).order_by('-created')
    # OpenWeatherAPI
    req = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={station[0]["lat"]}&lon={station[0]["lng"]}&appid=a23ab512a84332d31ac33b0fd3c9fc90&units=metric&lang=NL&exclude=minutely,hourly,daily,alerts')
    weather = req.json()['current']['weather'][0]['description']
    temp = round(req.json()['current']['temp'])
    args = {'station': station, 'station_name': station_name, 'messages': messages, 'weather': weather, 'temp': temp}
    return render(request, 'station.html', args)

def station_get_messages(request, id):
    station = [i for i in data if i['UICCode'] == id]
    messages = Message.objects.filter(station=station[0]['UICCode'], approved=True).order_by('-created')[:5]
    args = {'messages': messages}
    return render(request, 'partials/get_messages.html', args)

def station_get_forecast(request, id):
    station = [i for i in data if i['UICCode'] == id]
    req = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={station[0]["lat"]}&lon={station[0]["lng"]}&appid=a23ab512a84332d31ac33b0fd3c9fc90&units=metric&lang=NL&exclude=current,minutely,daily,alerts')
    forecast = [{'dt': datetime.datetime.fromtimestamp(i['dt']), 'temp': round(i['temp']), 'icon': f'http://openweathermap.org/img/wn/{i["weather"][0]["icon"]}@2x.png'} for i in req.json()['hourly'][:5]]
    args = {'forecast': forecast}
    return render(request, 'partials/get_forecast.html', args)
def station_get_departures(request, id):
    station = [i for i in data if i['UICCode'] == id]
    headers = {'Ocp-Apim-Subscription-Key': settings.NS_API_KEY, }
    params = urllib.parse.urlencode({'uicCode': station[0]['UICCode'], 'maxJourneys': 5, })
    conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
    conn.request("GET", "/reisinformatie-api/api/v2/departures?%s" % params, "{body}", headers)
    response = conn.getresponse()
    departures = [
        {'direction': i['direction'],
         'plannedDateTime': datetime.datetime.strptime(i['plannedDateTime'], "%Y-%m-%dT%H:%M:%S%z"),
         'actualDateTime': datetime.datetime.strptime(i['actualDateTime'], "%Y-%m-%dT%H:%M:%S%z"),
         'overTime': round((datetime.datetime.strptime(i['actualDateTime'],
                                                       "%Y-%m-%dT%H:%M:%S%z") - datetime.datetime.strptime(
             i['plannedDateTime'], "%Y-%m-%dT%H:%M:%S%z")) / datetime.timedelta(minutes=1)),
         'plannedTrack': None if not 'plannedTrack' in i else i['plannedTrack'],
         'longCategoryName': i['product']['longCategoryName'],
         'operatorName': i['product']['operatorName'],
         'routeStations': [j['mediumName'] for j in i['routeStations']],
         'cancelled': i['cancelled'],
         'message': i['messages'][0]['message'] if i['cancelled'] else None
         }
        for i in json.loads(response.read().decode('utf-8'))['payload']['departures']]
    conn.close()
    args = {'departures': departures}
    return render(request, 'partials/get_departures.html', args)
def station_get_facilities(request, id):
    accepted_facilities = ['Toilet', 'SANIFAIR Toilet', 'P+R gratis', 'P+R betaald', 'Lift', 'OV-fiets']
    weekday = datetime.datetime.today().weekday()
    station = [i for i in data if i['UICCode'] == id]
    headers = {'Ocp-Apim-Subscription-Key': settings.NS_API_KEY, }
    params = urllib.parse.urlencode({'limit': '150', 'radius': '1000', 'lang': 'nl', 'screen-density': 'ios-2.0', 'details': 'false', 'station_code': station[0]['code'],})
    conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
    conn.request("GET", "/places-api/v2/places?%s" % params, "{body}", headers)
    response = conn.getresponse()
    facilities = [{'name': i['name'],
                   'listLogoImage': i['listLogoImage']['uri'],
                   'open': None if i['open'] == 'Unknown' else True if i['open'] == 'Yes' else False,
                   'nextOpeningTime': None if not 'openingHours' in i else i['openingHours'][weekday+1 if weekday != 6 else 0]['startTime'],
                   'nextClosingTime': None if not 'openingHours' in i else i['openingHours'][weekday]['endTime'],
                   'rentalBikes': None if not i['name'] == 'OV-fiets' else 'Aantal niet bekend' if not 'rentalBikes' in i['locations'][0]['extra'] else f"{sum([int(j['extra']['rentalBikes']) for j in i['locations']])} beschikbaar"
                  }
                for i in json.loads(response.read().decode('utf-8'))['payload'] if i['name'] in accepted_facilities]
    conn.close()
    args = {'facilities': facilities}
    return render(request, 'partials/get_facilities.html', args)

def station_get_disruptions(request, id):
    station = [i for i in data if i['UICCode'] == id]
    headers = {'Ocp-Apim-Subscription-Key': settings.NS_API_KEY, }
    params = urllib.parse.urlencode({})
    conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
    conn.request("GET", f"/reisinformatie-api/api/v3/disruptions/station/{station[0]['code']}?%s" % params, "{body}", headers)
    response = conn.getresponse()
    disruptions = [{'cause': i['timespans'][0]['cause']['label'],
                    'situation': i['timespans'][0]['situation']['label'],
                    'additionalTravelTime': None if not 'additionalTravelTime' in i['timespans'][0] else i['timespans'][0]['additionalTravelTime']['maximumDurationInMinutes'],
                    'type': i['type'],
                   }
                   for i in json.loads(response.read().decode('utf-8'))]
    conn.close()
    args = {'disruptions': disruptions}
    return render(request, 'partials/get_disruptions.html', args)

def station_message(request, id):
    station = [i for i in data if i['UICCode'] == id]
    station_name = station[0]['namen']['lang']
    form = MessageForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            message = Message()
            message.name = form.cleaned_data.get('name') if form.cleaned_data.get('name') else 'Anoniem'
            message.message = form.cleaned_data.get('message')
            message.station = station[0]['UICCode']
            message.approved = None
            if not form.errors:
                message.save()
                return redirect('station_message', station[0]['UICCode'])
    args = {'station': station, 'station_name': station_name, 'form': form}
    return render(request, 'station_message.html', args)

def admin(request):
    messages = Message.objects.all().order_by('-created')
    unreviewed_count = Message.objects.filter(reviewed=None).count()
    args = {'data': data ,'messages': messages, 'unreviewed_count': unreviewed_count}
    return render(request, 'admin.html', args)

def admin_mod(request, id=None):
    if request.method == 'POST':
        message = Message.objects.get(pk=id)
        message.approved = True if request.POST.get('approval') == '1' else False
        message.reviewed = timezone.now()
        message.moderator = request.user
        message.save()
        return redirect('admin_mod_get_message')
    else:
        return render(request, 'admin_mod.html')

def admin_mod_get_message(request):
    try:
        message = Message.objects.filter(reviewed=None).order_by('created')[0]
        station = [i for i in data if i['UICCode'] == message.station]
        station_name = station[0]['namen']['lang']
        unreviewed_count = Message.objects.filter(reviewed=None).count()
        args = {'message': message, 'station_name': station_name, 'unreviewed_count': unreviewed_count}
        return render(request, 'partials/message.html', args)
    except IndexError:
        return HttpResponse('Geen berichten om te beoordelen')

def admin_login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user and user.is_active:
                login(request, user)
                request.session.set_expiry(0)
                return redirect('home')
            else:
                form.add_error(None, 'Onjuist email adres of wachtwoord')
    args = {'form': form}
    return render(request, 'login.html', args)

def admin_logout(request):
    auth.logout(request)
    return redirect('login')