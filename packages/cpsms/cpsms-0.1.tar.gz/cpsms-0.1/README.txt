THIS IS:
A Python wrapper around the SMS gateway from CPSMS <https://www.cpsms.dk/>.

THIS IS NOT:
Some sort of magic, free SMS gateway.

You need to have a (paid) account at CPSMS to be able to use their gateway.
They sell a fair, no-nonsense product which I'd recommend if you want to be
able to send SMS from your code (primarily to Danish phones).

See a couple of example use cases in example.py that should have come
along with this file. Apart from what is shown in examples.py, this also
supports status callback URLs, delayed sending and flash messages.

For more info on parameters, take a look at the API documentation found at:
<https://www.cpsms.dk/login/index.php?page=dokumentation>.

I believe the gateway software running at the CPSMS server is some sort	of
standard product. This may be able to talk to other remote SMS gateways as
well, and that's why I made it an option to specify another gateway base
URL. If you know of any other compatible gateways, please let me know, and
I'll list them in the README.
