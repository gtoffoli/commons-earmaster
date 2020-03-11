# commons-earmaster
Estending the CommonS platform (*CommonSpaces*) for Projects using **EarMaster**

The [CommonS platform](https://github.com/gtoffoli/commons) sends its internal *activity stream* to an **xAPI LRS**.
It also allows the user to self-declare with xAPI statements *learning experiences* done outside.
This small Django application allows the *Supervisor* of a *Project*, for different project members, to load a CSV file exported from the *EarMaster* music application and to send to the xAPI LRS statements representing the musical exercises and achievements logged by EarMaster.
