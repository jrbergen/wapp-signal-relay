=================
wapp-signal-relay
=================
Relays Whatsapp messages to Signal for specified groups and/or contacts.

============
What and why
============

Whilst trying to transition to Signal, group chats between Signal and Whatsapp can become desynchronized, potentially leaving
Signal users with a negative experience. To ammeliorate that annoyance, this project intends to use
`signal-cli-rest-api <https://github.com/SebastianLuebke/signal-cli-rest-api.git>`__ and a yet to be determined Whatsapp API to relay messages from specified WhatsApp chats/groups to Signal. (Apparently people have been
`getting their phone number banned <https://news.ycombinator.com/item?id=18897705>`__ from WhatsApp registering their
number with APIs like 'yowsup'. See also `these takedowns <https://github.com/github/dmca/blob/332f1896902c4f5780a249c0be5a22b75a4d784e/2014/2014-02-12-WhatsApp.md>`.

Thus, this software is intended to help ease the transition from Whatsapp to Signal by at least having the Signal chats be up-to-date for everyone in the group. Note that there are no plans to implement relay functionality from Signal to Whatsapp, as that would defeat the primary purpose of using Signal in the first place. 

### Note: use of separate phone number is advisable
Note that an active phone number is required to register for both Whatsapp and Signal. Furthermore, to the best of my knowledge WhatsApp allows your phone number to be used on a single device only, and using web Whatsapp requires one to be in the same network (please let me know if this is incorrect). Hence, using your current phone number will likely interfere with your daily phone usage. To overcome that, one could for instance register a cellular enabled device - like an old phone - with a prepaid SIM-card, and create a seperate user used to relays group messages.
