import requests
import telegram
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio credentials
account_sid = 'ACc3fdea95870c434343f572fb98d27fad'
auth_token = '935c2b91b2e6c4b0e227b23da9c01097'

# Twilio WhatsApp number and recipient number
whatsapp_number = 'whatsapp:+14155238886'  # Twilio's Sandbox number
recipient_numbers = ['whatsapp:+4917630179560',
                     'whatsapp:+491625988345']  # our WhatsApp number

# Initialize Twilio Client
client = Client(account_sid, auth_token)


def send_whatsapp_message(date, type, value):
  message_body = f'BTC {type} Liquidation  at {date} is {value}'
  # Send a WhatsApp message
  for recipient_number in recipient_numbers:
    message = client.messages.create(body=message_body,
                                     from_=whatsapp_number,
                                     to=recipient_number)
    print(f"Message sent to {recipient_number}: {message.sid}")


def make_api_call(symbols,
                  interval,
                  from_timestamp,
                  to_timestamp,
                  convert_to_usd="true"):
  # Define the API endpoint

  api_url = "https://api.coinalyze.net/v1/liquidation-history"

  # Construct the query parameters
  params = {
      "symbols": symbols,
      "interval": interval,
      "from": from_timestamp,
      "to": to_timestamp,
      "convert_to_usd": convert_to_usd
  }
  headers = {
      "api_key": api_key  # Replace with the actual API key header name
  }
  try:
    # Make the API call
    response = requests.get(api_url, params=params, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200 and response.json() != []:
      # Parse and handle the response data
      data = response.json()
      print(data)
      # Process the data as needed
      for entry in data[0]['history']:
        timestamp = entry['t']
        l_value = entry['l']
        s_value = entry['s']

        # Convert Unix timestamp to a readable date
        date_time = datetime.utcfromtimestamp(timestamp)
        formatted_date = date_time.strftime('%Y-%m-%d %H:%M')

        print(
            f"Timestamp: {formatted_date}, Long Liquidation: {l_value}, Short Liquidation: {s_value}"
        )
        if l_value > 300000:
          send_whatsapp_message(formatted_date, "long", l_value)
        elif s_value > 150000:
          send_whatsapp_message(formatted_date, "short", s_value)
    else:
      #print(data)
      # Print an error message if the request was not successful
      print(f"Error: {response.status_code} - {response.text}")

  except requests.RequestException as e:
    # Handle any exceptions that may occur during the request
    print(f"Error: {e}")


# Example usage:
api_key = "c3c04062-7925-49bf-8f94-dbcc977da258"
symbols = "BTCUSDT_PERP.A"
interval = "5min"
# from_timestamp = 1703922731  # Replace with your actual from timestamp
# to_timestamp = 1703968203  # Replace with your actual to timestamp
to_timestamp_limit = 1734767531  #21-12-2024

# Calculate timestamps for the last 5 minutes
current_time = datetime.now().timestamp()  # Current timestamp
print(current_time)
to_timestamp = int(
    current_time // 300) * 300  # Round down to the nearest 5 minutes
from_timestamp = to_timestamp - 600  # Previous 5 minutes

# Convert timestamps to readable dates
from_date = datetime.utcfromtimestamp(from_timestamp).strftime(
    '%Y-%m-%d %H:%M:%S')
to_date = datetime.utcfromtimestamp(to_timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Example output of timestamps and dates for the last 5 minutes
print(f"From Timestamp (Last 5 mins): {from_timestamp}, Date: {from_date}")
print(f"To Timestamp (Current Time): {to_timestamp}, Date: {to_date}")

make_api_call(symbols, interval, from_timestamp, to_timestamp)