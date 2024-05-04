# OpenSplitBot

<img src="assets/OpenSplit_logo.jpeg" alt="OpenSplit Logo" width="300"/>

## What is OpenSplitBot?

OpenSplitBot is a bot designed to **help groups of people manage joint expenses and minimize the number of transfers** when balancing accounts.

To do this, instead of a mobile or web application, OpenSplit **integrates into any Telegram group** without the need for external applications, allowing all group members to **review the current group balance, add new expenses and show the movements to be made to balance**. Users can contact the bot in individual chats, allowing them to **know their balance in all OpenSplit groups they belong to**.


In addition, **OpenSplit has a web interface that allows to centralize the information of all the groups to which it belongs**. Authentication is done through Telegram, so no new account is required. What are you waiting for to start using OpenSplit?

## Usage
Getting started with OpenSplitBot is as simple as typing its “OpenSplit” in the Telegram search engine and adding it to the group where we want it to help us.

Once added, OpenSplit will automatically register the group in its database, and you're ready to wait to use it. The commands offered by OpenSplitBot are as follows:

- <a>/help</a>: Lists all commands along with a brief description of them.
- <a>/add_expense</a>: OpenSplitBot will start a guided conversation that allows you to add a new expense (name, payer, amount and receivers) to the group database.
- <a>/balance</a>: Displays the current balance of the group members.
- <a>/calculate_exchanges</a>: OpenSplitBot calculates for you the most efficient moves to balance the books.
- <a>/web_login</a>: OpenSplitBot allows you to open our web interface, which centralizes all the information of the groups you belong to.

## Other parts of the project

Actually, OpenSplitBot is not only this project, but it is made up of two other equally (or almost) important parts:

- The backend, which is in charge of storing data, returning queries and performing optimization calculations. More detailed information about it (such as that it has been implemented in Rust!) can be found in its [repository](https://github.com/CastilloDel/OpenSplitBackend). 

- The frontend, which forms the web interface of OpenSplit, and allows a better visualization of the data. More details can be found in its [repository](https://github.com/DaniPVargas/OpenSplitFrontend).
