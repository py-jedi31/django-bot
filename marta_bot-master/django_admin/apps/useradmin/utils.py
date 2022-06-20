"""В разработке"""
# import random
#
# from django_admin.apps.useradmin.models import LinkPassword
#
#
# def get_new_password():
#     chars = '+-/*!&$#@?=@<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
#     password = "".join([random.choice(chars) for i in range(8)])
#     if password in LinkPassword.objects.all():
#         password = get_new_password()
#         return password
#     LinkPassword.objects.create(password=password)
#     return password

