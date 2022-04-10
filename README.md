# HOTEL-OG-BOT🌎
This is my first experience, so, it should be not ideal. If you find it interesting or you find some mistakes - please, write me, because it is important for me.

![Photo in Telegram](https://sun9-83.userapi.com/impf/dvTTyS9O0WcBujSHE7d_0pXv9vmHOdueTjdFcQ/xdcG8-6quIc.jpg?size=561x560&quality=95&sign=67b781a54fb09428e3c74f74b100f572&type=album)
---
## Content
1. [Bot description](#Bot_description)
2. [Project structure](#Project_structure)
3. [Contacts](#Contacts)
---
## Bot description <a name="Bot_description"></a> 
This bot uses the API from https://rapidapi.com/hub, exactly API Hotels in category Travel APIs

![Travel API photo](https://rapidapi-prod-apis.s3.amazonaws.com/a3/303bef2f1d4ec3aac54f81300fd241/4d9a73815653a59282b403df62d2fbaf.png)

### Bot commands:
1. /lowprice - the cheapest hotels
2. /highprice - the most expensive hotels
3. /bestdeal - here you can select a price range and specify the distance to the center
4. /history - here you can see your history in several modes
5. /mail - here you can add your email (used to send the story to the email)

### Logic (Steps) in use <a name="steps"></a>
1. Find him in Telegram - @HOTEL_OG_BOT
2. Send him '/start
3. You will see something like that, so now we need to select the command from his list.
![image](https://user-images.githubusercontent.com/92817776/162619496-15e43188-2b96-4683-aded-ee2fca558f77.png)
4. Ok, now we need to select the city in which we will look for hotels
![image](https://user-images.githubusercontent.com/92817776/162619826-ce80f11c-595b-414f-9b7a-1a0776e85e8e.png)
5. Let it be London, now we need to clarify country of our 'London'
![image](https://user-images.githubusercontent.com/92817776/162620204-b81e32ef-239a-4755-810b-5cd3b1b94604.png)
6. I meant England, now we need to select our arrival date (check-in date)
![image](https://user-images.githubusercontent.com/92817776/162620245-6b446abd-8079-40df-9b22-1b97f7951eac.png)
7. For instance, I'm going to check into a hotel tomorrow, so I've selected the second button ('Завтра'). Now we need to select our departure date (check-out date)
![image](https://user-images.githubusercontent.com/92817776/162620388-6a1417a7-3300-42b2-844a-72956d9857a4.png)
8. Congrat's, we did it!
![image](https://user-images.githubusercontent.com/92817776/162620499-0b67023b-66bd-4cf7-ab9c-7642c13e8e84.png)

### Hotel Information <a name="info"></a>
- Name of the hotel
- Address of the hotel
- Rating of the hotel
- Distance to the some landmark
- Distance to the center
- Price per night
- Total price (Price per night * (check-out date - check-in date))

## Project structure <a name="Project_structure"></a> 

- BotMain
    - hotels_iterator.py (Here you can find the logic of composing a message with hotel [info](#info))
    - main.py (Here you can find the [logic](#steps) of using the bot
 
- Classes (nothing special, a description of the necessary classes)
    - bd_iter.py (class of multi-directional iterator)
    - city.py (class of the city)
    - command.py (class of the user commands)
    - history.py (encapsulation of working with a database)
    - hotel.py (class of the hotel with some necessary info)
    - telegram_user.py (class of the TelegramUser)
  
- CreatingQueries (nothing special, you also can check the documentation in the code)
    - headers.py
    - photos_api.py
    - search_city.py
    - search_hotels
 
Other:
- db.py (connecting to a database and mailbox)
- requirements.txt
- ThankYou.png

## Contacts <a name="Contacts"></a> 
You can contact me in the following ways:

My E-mail: neweternalicon@gmail.com

My Telegram: @youngvishes

❤Thank you❤
