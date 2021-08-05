from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from apps.accounts.models import User
from apps.dialogs.models import Thread, Message


class ThreadTestCase(APITestCase):
    def setUp(self) -> None:
        participants = []
        for i in range(1, 3):
            user = User.objects.create(
                username=f"test{i}",
                first_name=f"Name{i}",
                last_name=f"Lname{i}",
                email=f"test{i}@com",
            )
            user.set_password(f"testPassword")
            user.save()
            participants.append(user)

        self.thread = Thread.objects.create()
        self.thread.participants.set(participants)

        self.message = Message.objects.create(
            text="hello", thread=self.thread, sender=self.thread.participants.first()
        )

    def _get_user_token(self, email="test@example.com", password="testPassword"):
        login_url = reverse("dialogs:api-token-auth")
        response = self.client.post(
            login_url,
            {"email": email, "password": password},
            format="json",
        )
        response_data = response.json()

        return "JWT {}".format(response_data.get("token", ""))

    def test_threads_list(self):
        threads_list_url = reverse("dialogs:threads_list")
        user = User.objects.first()
        # Positive test with authentication user
        result = self.client.get(
            threads_list_url, HTTP_AUTHORIZATION=self._get_user_token(email=user.email)
        )
        self.assertEqual(result.status_code, 200)
        # Check that last message in data equal our message
        self.assertEqual("hello", result.data.get("results")[0].get("last_message"))
        # Check that count in data equal our count
        self.assertEqual(1, result.data.get("results")[0].get("count_unread"))
        # Negative test with not authentication user
        result = self.client.get(
            threads_list_url, HTTP_AUTHORIZATION=self._get_user_token()
        )
        self.assertEqual(result.status_code, 401)

    def test_create_thread(self):
        create_thread_url = reverse("dialogs:create_thread")
        user = User.objects.first()
        # Positive test with authentication user
        result = self.client.post(
            create_thread_url,
            {"participants": [1, 2]},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual(result.status_code, 201)
        # Negative test with not authentication user
        result = self.client.post(
            create_thread_url,
            {"participants": [1, 2]},
            HTTP_AUTHORIZATION=self._get_user_token(),
        )
        self.assertEqual(result.status_code, 401)

    def test_get_single_thread(self):
        thread_url = reverse("dialogs:single_thread", kwargs={"pk": 1})
        user = User.objects.first()
        # Positive, get single thread
        result = self.client.get(
            thread_url, HTTP_AUTHORIZATION=self._get_user_token(email=user.email)
        )
        self.assertEqual(result.data.get("id"), 1)
        self.assertEqual(result.status_code, 200)
        user = User.objects.create(
            username=f"test0",
            first_name=f"Name0",
            last_name=f"Lname0",
            email=f"test0@com",
        )
        user.set_password(f"testPassword")
        user.save()
        # Negative, if user not in Thread
        result = self.client.get(
            thread_url, HTTP_AUTHORIZATION=self._get_user_token(email=user.email)
        )
        self.assertEqual(result.status_code, 404)

    def test_update_thread(self):
        create_thread_url = reverse("dialogs:create_thread")
        update_thread_url = reverse("dialogs:update_thread", kwargs={"pk": 1})
        user = User.objects.first()
        # Positive, update thread
        result = self.client.patch(
            update_thread_url,
            {"participants": [1]},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual(result.status_code, 200)
        created_thread = self.client.post(
            create_thread_url,
            {"participants": [1, 2]},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        update_thread = self.client.patch(
            update_thread_url,
            {"participants": [1]},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertNotEqual(created_thread.data, update_thread.data)
        user = User.objects.create(
            username=f"test0",
            first_name=f"Name0",
            last_name=f"Lname0",
            email=f"test0@com",
        )
        user.set_password(f"testPassword")
        user.save()
        # Negative, if user not in Thread
        result = self.client.patch(
            update_thread_url,
            {"participants": [1]},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual(result.status_code, 404)


class MessageTestCase(APITestCase):
    def setUp(self) -> None:
        participants = []
        for i in range(1, 4):
            user = User.objects.create(
                username=f"test{i}",
                first_name=f"Name{i}",
                last_name=f"Lname{i}",
                email=f"test{i}@com",
            )
            user.set_password(f"testPassword")
            user.save()
            participants.append(user.id)

        self.thread = Thread.objects.create()
        self.thread.participants.set(participants[:2])
        for i in range(5):
            Message.objects.create(
                text=f"test{i}",
                thread=self.thread,
                sender=self.thread.participants.first(),
            )

    def _get_user_token(self, email="test@example.com", password="testPassword"):
        login_url = reverse("dialogs:api-token-auth")
        response = self.client.post(
            login_url,
            {"email": email, "password": password},
            format="json",
        )
        response_data = response.json()

        return "JWT {}".format(response_data.get("token", ""))

    def test_message_list(self):
        messages_list_url = reverse("dialogs:messages_list", kwargs={"pk": 1})
        user = User.objects.first()
        result = self.client.get(
            messages_list_url, HTTP_AUTHORIZATION=self._get_user_token(email=user.email)
        )
        # Positive tests
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data.get("count"), 5)
        user = User.objects.last()
        # Negative tests
        result = self.client.get(
            messages_list_url, HTTP_AUTHORIZATION=self._get_user_token(email=user.email)
        )
        self.assertEqual(result.status_code, 404)
        self.assertIn("You have not permission", result.data.get("detail"))

    def test_edit_message_or_status(self):
        create_message_url = reverse("dialogs:create_message")
        edit_messages_or_status_url = reverse(
            "dialogs:edit_message_or_status", kwargs={"pk": 1}
        )
        user = User.objects.first()
        # Positive tests
        create_message = self.client.post(
            create_message_url,
            {"text": "test00", "thread": self.thread, "sender": user.id},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        update_message = self.client.patch(
            edit_messages_or_status_url,
            {"text": "test01"},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertNotEqual(create_message.data, update_message.data)
        self.assertEqual(update_message.data.get("text"), "test01")
        self.assertEqual(update_message.status_code, 200)

        user = User.objects.last()
        # Negative tests
        result = self.client.patch(
            edit_messages_or_status_url,
            {"text": "test01"},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertIn("You have not permission", result.data.get("detail"))

    def test_create_message(self):
        create_message_url = reverse("dialogs:create_message")

        user = User.objects.first()
        # Positive
        result = self.client.post(
            create_message_url,
            {"text": "test00", "thread": self.thread, "sender": user.id},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual(result.status_code, 201)
        user = User.objects.last()
        # Negative, wrong user
        result = self.client.post(
            create_message_url,
            {"text": "test00", "thread": self.thread, "sender": user.id},
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual("You have not permission", result.data.get("detail"))

    def test_delete_message(self):
        delete_message_url = reverse("dialogs:delete_message", kwargs={"pk": 1})

        user = User.objects.first()
        # Positive

        result = self.client.delete(
            delete_message_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertEqual(result.status_code, 204)
        # Negative, wrong pk
        wrong_delete_message_url = reverse("dialogs:delete_message", kwargs={"pk": 134})
        result = self.client.delete(
            wrong_delete_message_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=user.email),
        )
        self.assertIn("This object is not exist", result.data.get("detail"))
