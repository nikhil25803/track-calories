from fastapi.testclient import TestClient
import requests
from main import app
import unittest

client = TestClient(app)


class MyAPITestCase(unittest.TestCase):
    def test_read_main(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        url = "http://localhost:8000/user"

        # Create the data payload for the POST request
        data = {
            "name": "Nikhil Raj",
            "username": "nikhil25803",
            "email": "nikhil25803@gmail.com",
            "password": "password",
            "expected_calories": 10,
        }

        # Send the POST request
        response = requests.post(url, json=data)

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Assert the response data
        created_user = response.json()
        self.assertEqual(created_user["name"], "Nikhil Raj")
        self.assertEqual(created_user["username"], "nikhil25803")
        self.assertEqual(created_user["email"], "nikhil25803@gmail.com")
        self.assertEqual(created_user["expected_calories"], 10)

    def test_login(self):
        url = "http://127.0.0.1:8000/user/login"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "",
            "username": "nikhil25803",
            "password": "password",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Assert the response status code
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Assertions of the responses
        self.assertIn("access_token", response_data)
        self.assertTrue(response_data["access_token"])
        self.assertIn("token_type", response_data)
        self.assertEqual(response_data["token_type"], "bearer")
        self.assertIn("user_id", response_data)
        self.assertIsInstance(response_data["user_id"], int)
        self.assertIn("username", response_data)
        self.assertIsInstance(response_data["username"], str)

        # ----------- Testing the Calories Logic with LoggedIn User --------------

        create_entry_endpoint = (
            f"http://127.0.0.1:8000/entry/{response_data['username']}/create"
        )

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {response_data['access_token']}",
            "Content-Type": "application/json",
        }

        """
        Case 1: In this case only the text is provided by the user, neither the calorie count nor the boolean value that if the daily
        the goal is accomplished or not

        In this case, Calorie is automatically fetched by the API and the daily goal is from the user database and add to the entry
        If the fetched calorie value is greater than the daily goal, it sets the *is_achieved* field as true.
        """

        data = {
            "text": "As the morning sun greeted me, I delighted in a scrumptious breakfast of fluffy pancakes, drizzled with golden maple syrup, crowned with a dollop of creamy whipped butter, and adorned with a colorful assortment of fresh berries."
        }

        new_entry_response = requests.post(
            create_entry_endpoint, headers=headers, json=data
        )
        new_entry_response_data = new_entry_response.json()
        self.assertEqual(new_entry_response.status_code, 200)
        self.assertEqual(new_entry_response_data["text"], data["text"])
        self.assertEqual(new_entry_response_data["is_achieved"], True)
        self.assertEqual(new_entry_response_data["calories_count"], 275.01)

        """
        Case 2: In this case, the text, as well as the calorie count, is entered by the user, hence it will not call the  API and just 
        add the value entered by the user.

        And same as prev, it also compares with the value daily goal value set by the user and updates the *is_achieved* field accordingly.
        """

        data = {
            "text": "Seeking a taste of the exotic, I savored the aromatic delight of a fragrant bowl of steaming hot pho, generously garnished with tender slices of beef, fresh herbs, bean sprouts, and a squeeze of zesty lime.",
            "calories_count": 50,
        }
        new_entry_response = requests.post(
            create_entry_endpoint, headers=headers, json=data
        )
        new_entry_response_data = new_entry_response.json()
        self.assertEqual(new_entry_response.status_code, 200)
        self.assertEqual(new_entry_response_data["text"], data["text"])
        self.assertEqual(new_entry_response_data["is_achieved"], True)
        self.assertEqual(new_entry_response_data["calories_count"], 50)

        """
        Case 3: In this case, all three values, text, calorie count, and the is_achieved value are provided.

        Without any API call, the new entry will be added to the database as per the value entered by the user. But the for the **is_achieved**
        column, a comparison will still be made, so that even if the users forget their daily goal, it will not affect the entry.
        """
        data = {
            "text": "As the morning sun greeted me, I delighted in a scrumptious breakfast of fluffy pancakes, drizzled with golden maple syrup, crowned with a dollop of creamy whipped butter, and adorned with a colorful assortment of fresh berries.",
            "calories_count": 150,
            "is_achieved": False,
        }
        new_entry_response = requests.post(
            create_entry_endpoint, headers=headers, json=data
        )
        new_entry_response_data = new_entry_response.json()
        self.assertEqual(new_entry_response.status_code, 200)
        self.assertEqual(new_entry_response_data["text"], data["text"])

        # Instead of false as per the user, it is still true !!
        self.assertEqual(new_entry_response_data["is_achieved"], True)
        self.assertEqual(new_entry_response_data["calories_count"], 150)

        # -------------------------- Delete the User Created for Test Only ---------------------
        delete_url = f"http://127.0.0.1:8000/user/{response_data['username']}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {response_data['access_token']}",
        }
        delete_user_endpoint = requests.delete(delete_url, headers=headers)
        delete_user_response = delete_user_endpoint.json()

        self.assertEqual(delete_user_endpoint.status_code, 200)
        self.assertEqual(
            delete_user_response["message"], "Deleted user with username: nikhil25803"
        )


if __name__ == "__main__":
    unittest.main()
