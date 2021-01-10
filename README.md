# CS50 Final Project: WeebTube - A community for anime enthusiasts

Flask web application

VIDEO LINK: https://youtu.be/1iaKTGvNpVI

## Requirements
Before running the web app using flask run, please cd into the downloaded WeebTubeProject folder. In order for WeebTube to send you an email with a temporary password, run the following lines in the terminal:

export MAIL_DEFAULT_SENDER="weebtubecs50@gmail.com"
export MAIL_PASSWORD="weebtube#456"
export MAIL_USERNAME="weebtubecs50"

You also need to install “flask_mail” and “password-generator.” This will require that you enter “pip3 install flask_mail” and “pip3 install random-password-generator” in the terminal, without the quotations used above. Alternatively, you may import all necessary libraries with “pip3 install -r requirements.txt” (without the quotations) in the terminal.

## Login
Upon running the web application, you will be redirected to the login page. If you have already registered for an account, you may input your username and password in order to log in and access the full site.

## Register
In order to register for an account, you will need to click on “Register” on the navigation bar while logged out. You will then be directed to a page which allows you to input a username (alphanumeric; max 20 characters), an email address, and a password (max 20 characters) in order to register for an account. You must enter the same password twice for confirmation. After successfully registering for an account, you will be redirected to the login page.

## Forgot Password
If you cannot remember your password, you may click on the “Forgot Password” link on the login page. You will then be directed to another page in which you should provide an existing username and matching email address to be given a temporary password via email. The email template will contain a greeting with your WeebTube account username and provide the temporary password which you should use to change your password unless you desire to keep your temporary password indefinitely as your current password. After you receive an email, an alert will appear near the top of the website, and you will be redirected to the change password page.

## Change Password
This page may be accessed via a link in the login page or after submitting information in the “Forgot Password” page. Regardless of how you arrive at the page, you - the user - must provide your username, current password, new password, and provide confirmation of your new password by typing it into another input box. Once submitted, you may use your new password to log in.

## Homepage
Upon logging into your account, you will arrive at the homepage. This page will always have a welcome message that contains hyperlinks to other pages in the site, namely the community, watch party, and your profile page. Below this welcome message is the top ten highest rated shows by users on the site. Even if two or more shows are ranked the same, the show that remained at that value the longest will be ranked higher. If you want to learn more about the shows, the table also has their cover images, episodes aired according to the 2018 MyAnimeList Kaggle Database (https://www.kaggle.com/azathoth42/myanimelist) extracted from MyAnimeList (https://myanimelist.net/), and their genres.

## Profile
You may access your profile through the navigation bar by clicking on “Account” and selecting “Profile” from the dropdown menu. Your profile displays your profile picture and information that you have provided about yourself in a container, your bio, five of your favorite anime under “Favorite Anime”, and three of your most recent ratings under “Recent Activity”. If you are a new user, your profile will have a generic profile picture, the date you joined will be displayed underneath your profile picture, and your bio will say “Welcome to my profile!”. In addition, your recent activity and favorite anime sections will be empty if you haven’t added any favorites or rated any anime yet. In order to view all of your favorite anime, you may click on the “View All” button next to “Favorite Anime” and travel to your “Favorites” page. In order to view your entire rating history, you may click on the “View All” button next to “Recent” and travel to your “Rating History” page. In order to edit your profile, you may click on the “Edit Profile” button next to “[your username]’s Profile” at the top of the profile. This button will direct you to a page that allows you to update some of the contents of your profile.

## Edit Profile
On the edit profile page, you may update your profile picture, bio, gender, and birthday. In order to update your profile picture, you have to input a valid image url (typically one that ends with an image file ending such as .jpg or .png) under “Update profile picture”. In order to change your bio, input what you would like your bio to say under “Edit bio”. You cannot change the date you joined the site. In order to change your gender, select one from the dropdown menu under “Gender”. If you do not want your gender displayed, select “Prefer not to say”. In order to change your birthday, input the correct date under “Birthday”. Once you’re done making changes to your profile, click the “Update Profile” button to save your changes and be redirected to your profile.

## Favorites
You may access your favorites list through your profile, as described previously, or through the navigation bar by clicking on “Account” and selecting “Favorites” from the dropdown menu. Your favorites page contains a table with all of your favorite anime. Each row contains the cover, title, episode count, season, and genres of one of your favorite anime. Near the top of the page are two buttons, “Add Favorites” and “Remove Favorites”.

## Add Favorites
Clicking on the “Add Favorites” button on your favorites page will direct you to a page that allows you to search for anime titles and add them to your favorites. A dropdown list of titles will appear and update based on what you have typed. You may either select one of these titles or reference them while typing in a full title in English or romanized Japanese. Once you’ve filled in the input with a valid title, you may click the “Update Favorites” button to add the title to your favorites. You cannot add more than 20 titles, as the update button will be disabled once 20 titles have been added. In order to go back to your favorites list you may click the “Back to favorites” link above the input or travel via the navigation bar.

## Remove Favorites
Clicking on the “Remove Favorites” button on your favorites page will direct you to a page that allows you to remove titles from your favorites. In order to remove a title, select a title from the dropdown list containing all of the titles of anime in your favorites and click the “Remove” button. In order to go back to your favorites list you may click the “Back to favorites” link or travel via the navigation bar.

## Friends
You may access your friend list through the navigation bar by clicking on “Interact with Friends” and selecting “Friends” from the dropdown menu. When selected, you will be directed to a page that allows you to send friend requests and view a table of all of your friends. Each row in the table contains a friend’s profile picture, username, the date they were friended, and a red button labeled “Unfriend” that allows you to unfriend the user. You may click on a friend’s profile picture or username to travel to their profile. In order to send a friend request, you may type in his/her username in the input box and click the “Add Friend” button. As you type in a username, a dropdown list with suggestions will appear. Directly above the friend table is a button that, when clicked, takes you to the section of your inbox which displays all incoming friend requests.

## Inbox
You may access your inbox through the navigation bar by clicking “Inbox”, which is located on the right side of the bar. Your inbox has three tables: one contains friend requests, another contains watch party requests, and the other contains the messages sent to you by friends. All tables are ordered so that the most recent requests or messages are on top. Each row in the “Friend Requests” table contains the username and profile picture of the requester, the date the request was sent, and two buttons, “Accept” and “Decline”, which allow you to respond to the request when clicked. Each row in the “Watch Party Requests” table contains the username and profile picture of the host, invite message, event details, date the request was sent, and two buttons, “Accept” and “Decline”, which allow you to respond to the request when clicked. Each row in the “Messages” table contains the username and profile picture of the sender, message, subject, date sent, and a button labeled “Remove” that, when clicked, deletes the message. You may click on a user’s profile picture or username to travel to their profile. The three buttons below the navigation bar - “Friend Requests”, “Watch Party Requests”, and “Messages” - send you to the corresponding section of the inbox when clicked. The inbox also contains two buttons labeled “Compose Message” and “Sent Messages”, respectively.

## Compose Message
You may select the “Compose Message” button in your inbox to travel to the page which allows you to compose a message. On this page, you may select the friend you wish to message from the dropdown list, add a subject if desired, and enter your message. Once you are ready to send your message, you may click the “Send” button. Upon sending, you will be redirected to your inbox.

## Sent Messages
You may select the “Sent Messages” button in your inbox to travel to a page containing all of the messages that you have previously sent. The most recent messages will be at the top of the table. Each row contains the username and profile picture of the recipient, message, subject, date sent, and a button labeled “Remove” that, when clicked, deletes the message. You may click on a user’s profile picture or username to travel to their profile. In addition, you may click on the “Back to inbox” link above the table to travel to your inbox.

## Rate a Show
Using the navigation bar at the top of any page of the website, you may find the “Rate a Show” tab. If clicked, you will be directed to the personal rating page in which you must enter the English or romanized Japanese title. The search engine will automatically update based on your input. To complete this section, you may either click on a title that is produced or type out the full English or romanized Japanese show title. After you fill in the title section, you must rate a show with an integer from 0 (inclusive) through 10. Below the rating input is the option to leave a comment. You may use this section to express your opinions and recommend other users to watch the show. The data from this page will then update your profile page, rating history page, and perhaps the homepage if your rating manages to raise or keep the show within the top ten highest rated shows on the site.

## Rating History
The rating history page stores the information collected in the “Rate a Show” page. You, the user, have the option of deleting the rating from your records, which would then update the history page, your profile page, and possibly the homepage if any of the top ten shows are impacted by your rating.

##Community
You may access the community page through the navigation bar by clicking on “Community”. On this page, you may view all of the users on WeebTube listed in alphabetical order in a table. Each row belonging to a user contains his/her profile picture, username, bio, date he/she joined WeebTube, and a button labeled “Visit Profile” that when clicked allows you to visit that specific user’s profile.

Every user’s profile is formatted in the same way as your profile aside from the “Edit Profile” button. You may view a user’s full favorites list and rating history in the same manner through his/her profile that you would your own through your own profile.

## Watch Party
To get to the watch party page, select the “Interact with Friends” tab on the navigation bar, the page title should appear in the dropdown. Once selected, you will be redirected to the watchparty page. Within this page, you are able to look at watch parties that you are attending (once you accept the host’s request via the inbox) or hosting. The hosting category has three subcategories: “Good to Go!”, “Pending,” and “All Invited Unavailable.” If at least one participant for a watch party accepts the request, the watch party details will appear in the “Good to Go!” table with the single participant and will update the participant list once others accept the invite. Other pending participants will remain in the “Pending” table. If all pending participants cancel after initially accepting the request or deny the requests upon invitation, the watch party will appear in the last table of the “Hosting” category. Within the table is a message for the host to cancel the party. One should also note that if the host cancels the watch party in either the first or second subcategories, the participants that accepted the invitation will no longer see the watch party in the “Participants” table. As for the host of the canceled watch party, all table rows (from “Good to Go! and/ or “Pending”) mentioning the same watch party will be removed.
Near the top of the page, there is a button to create a watch party. This will redirect you to a different page.

## Create a Watch Party
In order to create a watch party and send invitations to your friends, you must select at least one friend but no more than ten for the event. Next, you must provide insight as to what show you are planning to watch along with a kosmi room link because the event will be hosted via kosmi’s live video sharing services. Furthermore, you must schedule the date and time (Eastern Time). The user can also opt out of writing a personalized message to the friends they will send the request to, but the host’s friends will receive messages in their inbox with a default message. If you decide to write a personal message, you must provide the link for the event somewhere within the message. Regardless of the message, your invitation will be sent to your selected friends as pending.

## 404 Page Unknown
If you attempt to access a page that does not exist via the address bar, you will be redirected to a page displaying “Sorry! That page does not exist”. In order to proceed from here, choose a page to visit via the navigation bar or input a valid address.

## Log Out
In order to log out of your account, you may click “Log Out”, which is located on the right side of the navigation bar. Upon logging out, you will be redirected to the login page.
