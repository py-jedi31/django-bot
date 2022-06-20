# from pymongo import MongoClient
# try:
#     import settings
# except ModuleNotFoundError:
#     from bot_marta import settings
#
#
# client = MongoClient(settings.DATABASES["state"]["HOST"], int(settings.DATABASES["state"]["PORT"]))
# database = client[settings.DATABASES["state"]["NAME"]]
# user_state = database["aiogram_state"]
#
#
# def get_user_state(user_id: int):
#     """s"""
#     result = user_state.find_one({'user': user_id})
#     print(result)
#

# # get_user_state(915711775)
