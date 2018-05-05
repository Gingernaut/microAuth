
import sys
sys.path.append("./app")

import ujson
from locust import HttpLocust, TaskSet, task
from config import get_config

appConfig = get_config()

### Load testing. https://locust.io/

class WebsiteTasks(TaskSet):

    @task
    def index(self):
        self.client.get("/")


class WebsiteUser(HttpLocust):
    host = f"http://{appConfig.HOST}:{appConfig.PORT}"
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
