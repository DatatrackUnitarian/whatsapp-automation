from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://shahid:shahid0088@cluster0.aqyeu0n.mongodb.net/?retryWrites=true&w=majority")

db = cluster["bakery"]
users = db['users']
orders = db["orders"]
app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hi, Thanks for Contacting  *The Red Velvet*.\nYou can choose from one of the Options below:"
                    "\n*Type*\n1.To *Contact Us*\n 2. To *Order* snacks\n 3.To Know Our *Working Hours*\n 4."
                    "To Get Our *Address")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please Enter a Valid Response")
            return str(res)

        if option == 1:
            res.message(
                "You can Contact us through phone or email.\n\n*Phone: 990356 8581 \n*E-mail* : mail@bakery.com")
        elif option == 2:
            res.message("You have Entered *Ordering Mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following Cakes to order: \n\n1. Red Velvet \n2.DarkForest \n3. IceCream Cake"
                "\n4.Plum Cake \n5. SpongeCake \n6. Genoise Cake \n7. Angel Cake \n8. Carrot Cake \n9. Fruit Cake"
                " \n0. Go Back"
            )
        elif option == 3:
            res.message("We Work Everyday from *9AM to 9PM*")
        elif option == 4:
            res.message("We have multiple stores across the city. Our main center is at *4/54, Uttar para*")
        else:
            res.message("Please Enter a Valid Response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please Enter a Valid Response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}}
            )
            res.message("You can choose from one of the Options below:"
                        "\n\n*Type*\n\n1.To *Contact Us*\n 2. To *Order* snacks\n 3.To Know Our *Working Hours*\n 4."
                        "To Get Our *Address*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "dark Forest", "IceCream Cake", "Plum Cake", "SpongeCake ", "Genoise Cake",
                     "Angel Cake ", "Carrot Cake ", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}}
            )
            users.update_one(
                {"number": number}, {"$set": {"item": selected}}
            )
            res.message("Excellent Choice")
            res.message("Please Enter your Address to confirm the Order")
        else:
            res.message("Please Enter a Valid Response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks For shopping with us!")
        res.message(f"Your Order for {selected} has been received and will be delivered within an hour ")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}}
        )

    elif user["status"] == "ordered":
        res.message("Hi, Thanks for Contacting  again.\nYou can choose from one of the Options below:"
                    "\n*Type*\n1.To *Contact Us*\n 2. To *Order* snacks\n 3.To Know Our *Working Hours*\n 4."
                    "To Get Our *Address")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}}
        )

    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
