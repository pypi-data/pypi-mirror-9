# coding=utf8

from bluelake.client.sdk import BluelakeSDK

sdk = BluelakeSDK('sample', 'localhost:8000', sender='httplib')

print sdk.count(str='22')

sdk = BluelakeSDK('sample2', 'localhost:8000')

print sdk.count(str='22')
