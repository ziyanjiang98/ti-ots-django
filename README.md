# ti-ots-django
TI order tracking system (OTS) demo based on Django

OTS can be divided into four subsystems by the function it provides. They focus on their own functions, while interacting with each other to finish the whole process of PCB ordering.

Userinfo subsystem contains all user information of TI engineers and outer suppliers. All functions related to the user account, such as registration and information updates will be provided in this part. Order subsystem concentrates on the management of order information. Authority Subsystem controls the availability of resources in OTS. Every time a user requests an action on a resource will be checked with the permission in this subsystem. Lastly, Quote subsystem achieved the auction function following the rules in TI, allowing outer suppliers to quote for orders.
