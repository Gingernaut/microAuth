# import ujson
# import pytest


# class TestAdminAccount:

#     async def test_get_info(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.get("/account", headers=[("Authorization", jwt_token)])
#         res_data = await res.json()

#         assert res.status == 200
#         assert "jwt" not in res_data
#         assert res_data["emailAddress"] == "test@example.com"
#         assert res_data["userRole"] == "ADMIN"

#     async def test_valid_update(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         payload = {
#             "firstName": "thor",
#             "lastName": "odinson",
#             "userRole": "avenger"
#         }
#         res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(payload))
#         res_data = await res.json()

#         assert res.status == 200
#         assert res_data["success"] == "Account updated"
#         assert res_data["firstName"] == "Thor"
#         assert res_data["lastName"] == "Odinson"
#         assert res_data["userRole"] == "AVENGER"


#     async def test_access_all_accounts(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.get("/accounts", headers=[("Authorization", jwt_token)])

#         assert res.status == 200

        

#     async def test_access_specific_account(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.get("/accounts/1", headers=[("Authorization", jwt_token)])

#         assert res.status == 200

#     async def test_update_specific_account(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.get("/accounts/1", headers=[("Authorization", jwt_token)])

#         assert res.status == 200


#     async def test_access_nonexistent_account(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.get("/accounts/10000", headers=[("Authorization", jwt_token)])
#         res_data = await res.json()

#         assert res.status == 404
#         assert res_data["error"] == "User not found"


#     async def test_delete_other_account(self, test_server, create_account_jwt):
#         jwt_token = await create_account_jwt
#         res = await test_server.delete("/account", headers=[("Authorization", jwt_token)])
#         res_data = await res.json()

#         assert res.status == 200
#         assert res_data["success"] == "Account deleted"
