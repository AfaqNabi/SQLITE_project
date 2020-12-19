"""
Code was written solely by:
Afaq Nabi Lec A2 (nabi1)
Krutik Soni Lec A2 (ccid)
Natnail Ghebresilasie Lec A1 (ccid)
"""

import sqlite3
import getpass
import sys
import os
import time

conn = 0  # global connection
cursor = 0  # global cursor
invalid_char_array = [8, 9, 11, 32, 0, 27, 10, 13]  # if user enters any tabs, spaces etc
nothing = ['']  # if user enters nothing
padding = '-------+------------+--------------------------------+--------------------------' \
        '------+--------+----------------------+------------+--------------+'
# clear = lambda: os.system('cls')


def main():
    """
    main function everything starts here
    """
    global conn
    global cursor
    # python3 mmain.py bb

    print("SQLITE MINI-PROJECT 1\nAfaq Nabi\nNatnail Ghebresilasie\nKrutik Soni\nLOADING...")
    time.sleep(0.5)


    database_name = sys.argv[1]
    while database_name in nothing or ord(database_name[0]) in invalid_char_array:
        print("cannot enter nothing...")
        database_name = input('enter the name of the Database: ')
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    exitProgram = False

    # while loop to run the program while the user chooses not to exit
    while not exitProgram:
        login_SU = input('login(L), SignUp(S) or Exit(E): ')

        # make sure the user selects eitehr login or sign up only

        while login_SU.lower() not in ['l', 's', 'e']:
            login_SU = input('Enter valid input!\nlogin(L), SignUp(S) or Exit(E): ')

        # log the user in
        if login_SU.lower() == 'l':
            uid = login_user()

            print("Correct password!")
            logOut = False

            #while user doesnt choose to log out take the user to the after login screen options
            while not logOut:
                logOut, exitProgram = after_login(uid)


        # if new user sign them up
        if login_SU.lower() == 's':
            new_user()

        # if user wants to exit exit program
        if login_SU.lower() == 'e':
            exitProgram = True


def after_login(user_id):
    """
    Function that dictate the functions to be called based
    off of user input for what action they'd like to do
    """

    # keep asking for input till true
    user_input = input("Select an action...\nPost Question(P), Search for posts(S), Logout(L), Exit(E): ")
    while user_input.lower() not in ['p', 's', 'l', 'e']:
        user_input = input("invalid input\nSelect an action..."
                        "\nPost Question(P), Search for posts(S), Logout(L), Exit(E): ")

    # call the functions, make post, search post, logout, or exit based on user input
    #use pairs of bools to indicate if logout and exit conditions are matched
    if user_input.lower() == 'p':
        make_post(user_id, 'q', 1)
        return False, False
    elif user_input.lower() == 's':
        search_posts(user_id)
        return False, False
    elif user_input.lower() == 'l':
        print("Logging out...")
        time.sleep(1)

        return True, False
    elif user_input.lower() == 'e':
        print("Exiting Database...")
        time.sleep(0.4)

        return True, True


def make_post(user, Q_or_A, post_id):
    """
    Function to make a post based off of if the post
    is a question or an answer, get the users input for the post
    """


    # get user input for the post
    title = input("Title: ")
    while title in nothing or ord(title[0]) in invalid_char_array:
        print("you must enter a title")
        title = input("Title: ")

    body = input("Body: ")
    while body in nothing or ord(body[0]) in invalid_char_array:
        print("you must enter a body")
        body = input("Body: ")

    # find the number of posts to assign unique PID
    cursor.execute('''
                        select count(distinct posts.pid)
                        from posts
                        ''')
    x = cursor.fetchone()
    conn.commit()
    upid = x[0] + 1  # PID should be unique

    # check if the user making the post is posting a question(q) or answer(a)
    if Q_or_A == 'q':  # if posting question
        # insert the post into the posts table
        cursor.execute('''
        insert into posts (pid, pdate, title, body, poster)
        values(:pid, date('now'), :title, :body, :poster)
        ''', {'pid': upid, 'title': title, 'body': body, 'poster': user})
        conn.commit()

        # insert pid to the questions table also
        cursor.execute('''
        insert into questions(pid, theaid)
        values(:pid, NULL)
        ''', {'pid': upid})
        conn.commit()

    if Q_or_A == 'a':  # if posting answer
        cursor.execute('''
                    insert into posts(pid, pdate, title, body, poster)
                    values (:upid, date('now'), :title, :body, :poster)
                    ''', {'upid': upid, 'title': title, 'body': body, 'poster': user})
        conn.commit()

        # insert pid to the answers table also
        cursor.execute('''
                    insert into answers(pid, qid)
                    values (:pid, :qid)
                    ''', {'pid': upid, 'qid': post_id})
        conn.commit()

    print('Success!')
    time.sleep(1)


def return_posts(keywords):
    """Function to return the posts that the user wants based on the keyword/s"""
    posts = []

    # run a for loop of queries on the list of keywords entered to get the posts corresponding to the keywords
    for word in keywords:
        x = []
        # query to find title of posts
        cursor.execute('''
        SELECT posts.pid, posts.pdate, posts.title, posts.body, posts.poster, tags.tag, 
        max(votes.vno), count(DISTINCT(answers.pid))
        from posts left join tags on posts.pid = tags.pid
        left join answers on posts.pid = answers.qid
        left join votes on posts.pid = votes.pid
        where (posts.title like ?)
        group by posts.pid
        ''', ['%' + word + '%'])

        y = cursor.fetchall()
        conn.commit()
        for post in y:
            x.append(post)

        # query to find body fo posts
        cursor.execute('''
        SELECT posts.pid, posts.pdate, posts.title, posts.body, posts.poster, tags.tag, 
        max(votes.vno), count(DISTINCT(answers.pid))
        from posts left join tags on posts.pid = tags.pid
        left join answers on posts.pid = answers.qid
        left join votes on posts.pid = votes.pid
        where (posts.body like ?)
        group by posts.pid
        ''', ['%' + word + '%'])
        y = cursor.fetchall()
        conn.commit()

        #look for duplicate posts that are already used in title  but shouldnt also be used in body
        for post in y:
            append = True
            for pickedPost in x:
                if pickedPost[0] == post[0]:
                    append = False
            if append:
                x.append(post)

        for post in x:
            posts.append(post)

        # query to find the tags of posts
        cursor.execute('''
        SELECT posts.pid, posts.pdate, posts.title, posts.body, posts.poster, tags.tag, 
        max(votes.vno), count(DISTINCT(answers.pid))
        from posts left join tags on posts.pid = tags.pid
        left join answers on posts.pid = answers.qid
        left join votes on posts.pid = votes.pid
        where (tags.tag like ?)
        group by posts.pid
        ''', ['%' + word + '%'])
        y = cursor.fetchall()
        conn.commit()
        #put all posts in posts array that is returned after every keyword is searched
        for post in y:
            posts.append(post)

    # create dictionary and used posts array
    # orderedPosts is dictionary where key is post and value is the occurrence of each post
    # used posts array is array where each unique post is stored so it isnt reused when counting and adding it to the dictionary
    orderedPosts = {}
    usedPosts = []
    # loop where unique posts and counting or occurrence of each post is done
    # and stored in the dictionary and the used post array
    # putIn is a bool that indicates whether the current post in posts array has been added to the dictionary
    for post in posts:
        putIn = True
        counter = 0
        postID = post[0]
        for usedPost in usedPosts:
            if usedPost[0] == postID:
                putIn = False
        if putIn:
            for samePost in posts:
                if post[0] == samePost[0]:
                    counter += 1
            orderedPosts[post] = counter
            usedPosts.append(post)

    # orderes the dictionary keys by the value and stores it in decreasing order
    orderedPosts = {k: v for k, v in sorted(orderedPosts.items(), key=lambda item: item[1], reverse=True)}
    # initialize ordered array where only the posts should be stored in the correct order
    # done by the above stored function call on orderedPosts dictionary
    orderedArray = []

    #put each key which is a post into the array to be easily printed and iterated in next function
    for key in orderedPosts.keys():
        orderedArray.append(key)

    return orderedArray


def print_column_headers():

    head = ['PostID', 'postDate', 'postTitle', 'postBody', 'userID', 'tags', '# of votes', '# of answers']
    header = '{:>1} | {:10} | {:30} | {:30} | {:6} | {:20} | {:3} | {:3} |'.format(*head)
    print(padding)
    print(header)
    print(padding)


def search_posts(user_id):
    """
    Function to search the posts that the user wants based on the keywords
    """
    i = 0
    validInput = False
    keywords = input("Enter 1 or more keywords to search for a post: ")  # cant search for nothing

    # validate user input
    while keywords in nothing or ord(keywords[0]) in invalid_char_array:
        print("you must enter something")
        keywords = input("Enter 1 or more keywords to search for a post: ")  # cant search for nothing

    # put keywords in a list
    keyword_list = keywords.split()

    # find posts that match the keywords
    orderedArray = return_posts(keyword_list)

    # if no results found
    if orderedArray == []:
        print("no results found.")
        return None

    print_column_headers()  # print column headers

    # satisfy the five posts constraint
    # print posts until the 5th post is encountered
    # if the fifth post then give the user an option to enter a pid or continue to the next page
    # break is used to exit the for loop when user enters 'p'
    current5Posts = []
    for posted in orderedArray:

        #if its the 6th or 11th or ... posts it clears the current5posts array
        # print(current5Posts)
        # if i % 5 == 1:
        #     current5Posts.clear()

        #append current post into current5posts array
        current5Posts.append(posted)

        emp_list = []

        for k in posted:
            emp_list.append(str(k))

        final_post = answers_count(emp_list)
        post1 = '{:^6.5} | {:<10} | {:<30.30} | {:<30.30} | {:6.5} | {:20} | {:^10} | {:^12} |'.format(*final_post)
        print(post1)
        i = i + 1
        print(padding)

        if i % 5 == 0:
            nextPage = input('Type > for next page or P to enter PID: ')
            if nextPage in ['>', 'p']:
                validInput = True

            while not validInput:
                nextPage = input('Type > for next page or P to enter PID: ')

                if nextPage in ['>', 'p']:
                    validInput = True

            if nextPage == 'p':
                break
            elif nextPage == '>':
                current5Posts.clear()

    exitSearchInput = input("Would you like to look at a particular post? (Y/N) ")
    while exitSearchInput.lower() not in ['y', 'n']:
        exitSearchInput = input("Would you like to look at a particular post? (Y/N) ")

    if exitSearchInput.lower() == 'n':
        return None

    valid_pid = True

    #while loop keeps running untl valid pid is enttered
    while valid_pid:
        choice = input("Enter the pid of the post you want to view: ")
        while (choice in nothing) or ord(choice[0]) in invalid_char_array:
            print("invalid input")
            choice = input("Enter the pid of the post you want to view: ")

        #if user reached end of the posts then let user choose any post from the entire arrray
        if i == len(orderedArray):

            for pid in orderedArray:
                if pid[0] == choice:
                    valid_pid = False

            if valid_pid == True:
                print("Post ID is not in the printed Post ID's")

        # if user is choosing in between pages and not at the end then choose
        # only from the current 5 posts displayed
        else:
            for pid in current5Posts:
                if pid[0] == choice:
                    valid_pid = False

            if valid_pid == True:
                print("Post ID is not in the current 5 printed Post ID's")

    # call post_search() on the array based on if the user has reached the end of the
    # results and if they havent then only call post_search() on
    if i == len(orderedArray):
        post_search(user_id, choice, orderedArray)
    else:
        post_search(user_id, choice, current5Posts)


def answers_count(post):
    """
    check if the post is an answer and switch the # of answers to n/a
    """
    cursor.execute('''
                        select posts.pid
                        from posts, answers
                        where answers.pid = ?
                        ''', (post[0],))
    if_answer = cursor.fetchall()
    conn.commit()

    if if_answer == []:
        pass
    else:
        post[7] = 'N/A'
    return post


def post_search(user_id, choice, orderedArray):
    """
    This function is in charge of the actions available to
    a regular and a privileged user after a successful search of a post
    """
    # check if the user is privileged or not
    cursor.execute('''
                    select privileged.uid
                    from users, privileged
                    where privileged.uid = ?
                    ''', (user_id,))
    conn.commit()
    priv_user = cursor.fetchall()
    if priv_user == []:
        is_priv = False
    else:
        is_priv = True

    # check if the selected post is a question or answer
    cursor.execute(
        '''
            SELECT distinct posts.pid
            FROM posts, questions
            where posts.pid = questions.pid
            and questions.pid = ?
        ''', (choice,))

    question_id = cursor.fetchall()
    conn.commit()

    # if none is returned from query post must be a answer
    if question_id == []:
        is_question = False
    else:
        is_question = True

    vno = print_selected_post(choice, orderedArray)

    exitSearch = False
    possible_action = ['b', 't', 'e', 'q', 'v', 'a']

    # if is privileged user give more options
    if is_priv:
        print("You are a privileged user...")

        # if is questions
        if is_question:
            while not exitSearch:
                print("The selected post is a question")
                action = input("""You may give this question a badge(B), answer the question(A), give it a tag(T),
                                \redit the post(E), vote on the post(V),or quit the search(Q): """)
                while action.lower() not in possible_action:
                    print("invalid input")
                    action = input("""You may give this question a badge(B), answer the question(A), give it a tag(T),
                                    \redit the post(E), vote on the post(V),or quit the search(Q): """)
                exitSearch = searchPostControlFlow(action, user_id, vno, 'privileged and question', choice)

        # if is answer
        else:
            while not exitSearch:
                print("The selected post is an answer")
                action = input("""You may mark this answer as the accepted answer(A), give a badge(B),
                    \rgive a tag(T), you may edit post(E) or you may vote(V) or quit the search(Q): """)
                while action.lower() not in possible_action:
                    action = input(
                        """Invalid Input!\nYou may mark this answer as the accepted answer(A), give a badge(B), qgive a tag(T), you may edit post(E) or you may vote(V) or quit the search(Q): """)
                exitSearch = searchPostControlFlow(action, user_id, vno, 'privileged and answer', choice)

    # if regular user less choices
    else:
        while not exitSearch:

            # if is question
            if is_question:
                answer_vote = input("selected post is a question would you like to answer question(A) or vote(V): ")
                while answer_vote.lower() not in ['a', 'v', 'q'] or answer_vote in nothing:
                    print("invalid input")
                    answer_vote = input(
                        "selected post is a question would you like to answer question(A), vote(V) or quit the search(Q): ")
                exitSearch = searchPostControlFlow(answer_vote, user_id, vno, 'regular and question', choice)

            # if is answer
            else:
                question_vote = input(
                    "selected post is an answer would you like to vote? (y/n) or quit the search(Q): ")
                while question_vote.lower() not in ['y', 'n', 'q']:
                    print("invalid input")
                    question_vote = input(
                        "selected post is an answer would you like to vote? (y/n) or quit the search(Q): ")
                exitSearch = searchPostControlFlow(question_vote, user_id, vno, 'regular and answer', choice)


def print_selected_post(choice, orderedArray):
    """"
    Function to format the results of search post
    """
    vno = ''
    for posted in orderedArray:
        if posted[0] == choice:

            print('postID:        ', posted[0])
            print('postDate:      ', posted[1])
            print('postTitle:     ', posted[2])
            print('postBody:      ', posted[3])
            print("userID:        ", posted[4])
            print("tags:          ", posted[5])
            print("# of votes:    ", posted[6])
            print("# of answers:  ", posted[7])
            vno = posted[6]
            break
    if vno == None:
        return 0
    else:
        return vno


def searchPostControlFlow(actionInput, user_id, vno, priv, pid):
    """
    This function controls the flow of search post and the actions available
    """
    # control flow of the search posts actions
    # ['b', 't', 'e', 'q', 'v', 'a']
    if priv == 'privileged and question':

        if actionInput.lower() == 'a':
            make_post(user_id, 'a', pid)

        elif actionInput.lower() == 'b':
            return badge(pid)

        elif actionInput.lower() == 't':
            return add_tag(pid)

        elif actionInput.lower() == 'e':
            edit(pid)

        elif actionInput.lower() == 'v':
            return vote(user_id, pid, vno)

        elif actionInput.lower() == 'q':

            return True

    elif priv == 'privileged and answer':
        if actionInput.lower() == 'a':
            return mark(pid)

        elif actionInput.lower() == 'b':
            return badge(pid)

        elif actionInput.lower() == 't':
            return add_tag(pid)

        elif actionInput.lower() == 'e':
            edit(pid)

        elif actionInput.lower() == 'v':
            return vote(user_id, pid, vno)

        elif actionInput.lower() == 'q':
            return True

    elif priv == 'regular and question':
        if actionInput.lower() == 'a':
            make_post(user_id, 'a', pid)
        elif actionInput.lower() == 'v':
            return vote(user_id, pid, vno)
        else:
            return False
    elif priv == 'regular and answer':
        if actionInput.lower() == 'y':
            return vote(user_id, pid, vno)

    return True


def login_user():
    """
    This function will be called after a successful login while
    also making sure that the log in information provided is valid
    """
    truth_value = 0

    # validate user id and password
    while truth_value == 0:
        userID = input('userID: ')
        while userID in nothing or ord(userID[0]) in invalid_char_array:
            print("not a valid user id")
            userID = input('userID: ')
        unhashed_pass = getpass.getpass('Password: ')  # pass cannot be newline or space
        cursor.execute('''
                select users.pwd
                from users
                where users.uid = ?;
                ''', (userID,))
        pass_in_db = cursor.fetchall()
        conn.commit()
        if pass_in_db == []:
            print("Incorrect username or password")
            truth_value = 0
        elif unhashed_pass == pass_in_db[0][0]:
            truth_value = 1
        else:
            print("Incorrect username or password")
            truth_value = 0
    return userID


def new_user():
    """
    This function creates a new user in the database if the user
    exists already they'll be prompted to make a unique one till it's complete
    """

    print("signing up...")
    uid = input("enter a unique ID: ")
    while uid in nothing or ord(uid[0]) in invalid_char_array:
        print("you must enter a user id")
        uid = input("enter a unique ID: ")
    cursor.execute('''
    select count(users.uid)
    from users
    where users.uid = ? 
    ''', (uid,))
    a = cursor.fetchall()
    conn.commit()

    # validate user input
    while (a[0][0] != 0):
        uid = input("ID not unique, enter another unique ID: ")
        cursor.execute('''
        select count(users.uid)
        from users
        where users.uid = ? 
        ''', (uid,))
        a = cursor.fetchall()
        conn.commit()
    name = input("Name: ")

    while name in nothing or ord(name[0]) in invalid_char_array:
        print("you cannot enter nothing")
        name = input("Name: ")
    password = getpass.getpass('Password: ')  # prevent pass from being newline or space

    while password in nothing or ord(password[0]) in invalid_char_array:
        print("you cannot have zero characters in your password Try Again")
        password = getpass.getpass('Password: ')

    while ' ' in password:
        print("you cannot have a space in your password Try Again")
        password = getpass.getpass('Password: ')
    pwd = password
    city = input("City: ")

    while city in nothing or ord(city[0]) in invalid_char_array:
        print("you cannot enter nothing")
        city = input("City: ")

    # run querey to add user to database
    cursor.execute('''
            insert into users (uid, name, pwd, city, crdate)
            values (:uid, :name, :pwd, :city, date('now'));
            ''', {'uid': uid, 'name': name, 'pwd': pwd, 'city': city})
    conn.commit()
    print("Success!")
    time.sleep(0.5)



def vote(user, pid, vno):
    """This function is for making a successful vote on a post"""

    # run query to check if user has already voted
    cursor.execute('''
    select distinct votes.uid
    from posts, votes
    where votes.uid = ?
    and votes.pid = ?
    ''', (user, pid,))
    already_voted = cursor.fetchall()
    conn.commit()

    # if already voted return
    if already_voted == []:
        # if not voted add vote tot he data base
        cursor.execute('''
        insert into votes values(:pid,:vno,date('now'),:uid)
        ''', {'pid': pid, 'vno': int(vno) + 1, 'uid': user})
        conn.commit()
        print("success")
        return True
    else:
        print("you have already voted on this post")
        return True


def mark(pid):
    """
    This function is only for privelledged users where they're able to
    mark an answer as the accepted answer or replace the current accepted answer
    """
    cursor.execute('''
        Select answers.qid
        from answers
        where answers.pid = ?
        ''', (pid,))
    question = cursor.fetchall()
    conn.commit()
    theaid = question[0][0]
    # check if the post has an accepted answer already
    cursor.execute('''
        SELECT questions.theaid
        from questions, answers
        where questions.pid = ?
    ''', (theaid,))
    conn.commit()
    answers_id = cursor.fetchone()

    # if the post does not already have an accepted answer add it to the database
    if answers_id[0] == None:
        print("The post does not have an accepted answer")
        cursor.execute('''
                UPDATE questions
                SET theaid = ?
                WHERE pid = ?
            ''', (pid, theaid,))
        print("answer marked as accepted.")
        conn.commit()

    # if the post has an accepted answer prompt to change it
    else:
        choice = input("The post has an accepted answer, would you like to update it,(y/n) ")
        while choice.lower() not in ['y', 'n']:
            print("invalid input")
            choice = input("The post has an accepted answer, would you like to update it,(y/n) ")
        if choice.lower() == 'y':

            # update accepted answer
            cursor.execute('''
                UPDATE questions
                SET theaid = ?
                WHERE pid = ?
            ''', (pid, theaid,))

            conn.commit()
            print("accepted answer updated")

        elif choice.lower() == 'n':
            print("Accepted answer not updated...")
    return True


def add_tag(pid):
    """
    This function is only for privelledged users where they're
    able to add tags that are non-duplicate to a post
    """

    # gwet the tag from user and enter in database
    con = True
    while (con):
        choice = input("Enter the tag you would like to add or exit(e): ")
        while choice in nothing or ord(choice[0]) in invalid_char_array:
            print("invalid input")
            choice = input("Enter the tag you would like to add or exit(E): ")
        if choice.lower() == 'e':
            con = False
            return True
        cursor.execute('''
            SELECT tags.tag
            from tags, posts
            where tags.pid = ?
            and tags.tag like ?
        ''', (pid, '%' + choice + '%',))
        x = cursor.fetchall()
        conn.commit()
        while len(x) > 0:
            choice = input("You can not add a tag that's already been added, select a new tag to add: ")
            cursor.execute('''
                SELECT tags.tag
                from tags, posts
                where tags.pid = ?
                and tags.tag like ?
            ''', (pid, choice,))
            x = cursor.fetchall()
            conn.commit()
        cursor.execute('''
            INSERT INTO tags (pid, tag)
            VALUES (:pid, :tag)
        ''', {'pid': pid, 'tag': choice})
        conn.commit()


def edit(pid):
    """
    This function is for privileged users where they're able to
    edit the body and/or title of a post from search post
    """

    title_choice = input("Would you like to edit the title of the post, enter Y or N: ")
    if title_choice.lower() == 'y':
        new_title = input("Enter the new title: ")
        cursor.execute('''
            UPDATE posts
            SET title = ?
            WHERE posts.pid = ?
        ''', (new_title, pid))
        conn.commit()

    body_choice = input("Would you like to edit the body of the post, enter Y or N: ")
    if body_choice.lower() == 'y':
        new_body = input("Enter the new body: ")
        cursor.execute('''
            UPDATE posts
            SET body = ?
            WHERE posts.pid = ?
        ''', (new_body, pid))
        conn.commit()


def badge(pid):
    """
    This function is for privelledged users only where they're
    able to give a badge to a user that has a valid badge name
    """
    choice = input("Enter the badge name: ")
    while choice in nothing or ord(choice[0]) in invalid_char_array:
        print("Invalid Input")
        choice = input("Enter the badge name: ")

    cursor.execute('''
        SELECT COUNT(badges.bname)
        from badges
        where badges.bname like ?
    ''', ('%' + choice + '%',))
    x = cursor.fetchall()
    conn.commit()

    while (x[0][0] == 0):
        choice = input("That is not a valid badge name, enter a valid badge name or Exit(E): ")
        while choice in nothing or ord(choice[0]) in invalid_char_array:
            print("you must enter something")
            choice = input("That is not a valid badge name, enter a valid badge name or Exit(E): ")
        if choice.lower() in ['e']:
            print("no badges added")
            return True
        else:
            cursor.execute('''
                SELECT COUNT(badges.bname)
                from badges
                where badges.bname like ?
            ''', ('%' + choice + '%',))
            x = cursor.fetchall()
            conn.commit()

    # get the user who is recieving the badge
    cursor.execute('''
        SELECT posts.poster
        from posts
        where posts.pid = ?
    ''', (pid,))
    poster = cursor.fetchall()
    conn.commit()

    # However, two badges of the same class cannot be given to the same user on the same day.
    cursor.execute('''
        INSERT OR IGNORE INTO ubadges VALUES (:uid, date('now'), :bname)
    ''', {'uid': poster[0][0], 'bname': choice})
    conn.commit()


if __name__ == '__main__':
    main()
