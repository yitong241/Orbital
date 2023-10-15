from flask import Flask, render_template, request, redirect
#import configparser
#import requests
import os

def split_lines(lines):
    return list(map(lambda x: x.split(","),lines))

## DB boiler plates **
import sqlite3
def open_DB(db):
    connection=sqlite3.connect(db)
    connection.row_factory = sqlite3.Row
    return connection

app = Flask("__name__")
isAdmin = False

@app.route('/')
def root():
    return render_template('admin.html')

    
@app.route("/homepage")
def home():
    global isAdmin
    if isAdmin == False:
        redirect("/")
    else:
        con = open_DB('base.db')
        cur=con.execute("SELECT * FROM Venues")
        rows=cur.fetchall()
        print(rows)
        con.close()
    #return render_template("homepage.html",venues=rows)
    if isAdmin:
        return render_template('homepage.html', admin=admin, venues=rows)
    else:
        return render_template("admin.html", incorrect=True) 


@app.route("/help", methods=["GET"])
def show_help():
    return render_template("help.html")

@app.route("/links", methods=["GET"])
def add_link():
    if isAdmin == False:
        return redirect("/")
    else:
        try:
            con = open_DB('base.db')
            cur=con.execute("SELECT * FROM Venues")
            row=cur.fetchall()
            print(row)
            con.close()
        except Exception as e:
            print(str(e))
        con.close()
        for i in row:
            print(i)
        return render_template("links.html", venues = row)

@app.route("/add_links", methods=["POST"])
def add_links():
    if isAdmin == False:
        print("no admin")
        return redirect("/")
    else:
        try:
            con = open_DB("base.db")
            exit1 = (request.form.getlist('input-exit-1'))[0]
            exit2 = (request.form.getlist('input-exit-2'))[0]
            #print(exit1)
            #print(exit2)
            cur = con.execute("SELECT * FROM Exits WHERE location = ? AND exit = ?",(exit1,exit2))
            curr = cur.fetchall()
            if len(curr) != 0:
                pass
            elif exit1 == exit2:
                pass
            else:
                con.execute('INSERT INTO Exits VALUES(?,?)', (exit1, exit2))
                con.execute('INSERT INTO Exits VALUES(?,?)', (exit2, exit1))
                con.commit()
        except Exception as err:
            print(str(err))
        con.close()
        return redirect("/homepage")




@app.route("/venue", methods=["GET"] )
def show_venue_frm():
    con=open_DB("base.db")
    cur = con.execute('SELECT name FROM Venues')
    rows=cur.fetchall()
    con.close()
    return render_template("venue_frm.html", venues = rows)


@app.route('/admin', methods=['POST'])
def admin():
    global isAdmin
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('base.db')
    print(username)
    try:
        isAdmin = False
        cursor = conn.execute('SELECT * FROM Admins WHERE username=?', (username,))
        for row in cursor:
            #print(row[1])
            if password == row[1]:
                isAdmin = True
                break
            else:
                raise ValueError
    except:
        print('Username or password is incorrect.')
        conn.close()
        return render_template("admin.html", incorrect=True)
    else:
        conn.close()
        return redirect('/homepage')


@app.route("/add", methods=["POST","GET"])
def add_venue():
    if isAdmin == False:
        return redirect("/")
    else:
        con = open_DB("base.db")
        cur = con.execute('SELECT name FROM Venues')
        rows = cur.fetchall()
        con.close()
        image_file_name = ""
        if request.files['image'].filename == '':
            return render_template("venue_frm.html", noinput = True, venues = rows)
        #if "image" in request.files:
        else:
            image_file = request.files["image"]
            image_file_name=image_file.filename
            image_file.save("static/images/"+ image_file_name)
            #return render_template("venue_frm.html, noinput=True")
            
        try:
            exits = request.form.getlist('input-exit')
            #print("--------------------")
            #print(exits)
            #print(request.form["name"])
            if request.form["name"] != "" and request.form["description"] != "" and request.form["location"] != "":
                con=open_DB("base.db")
                con.execute("INSERT INTO Venues(Name, Description, Location, Image) " +
                            "VALUES(?,?,?,?)",
                            (request.form["name"], request.form["description"],request.form["location"],image_file_name))
                for eachExit in exits:
                    if eachExit != None:
                        con.execute('INSERT INTO Exits VALUES(?,?)', (request.form["name"], eachExit))
                        con.execute('INSERT INTO Exits VALUES(?,?)', (eachExit, request.form["name"]))
                con.commit()
            else:
                return render_template("venue_frm.html", notallinput = True, venues = rows)
        except Exception as err:
            print(str(err))
        con.close()
        return redirect("/homepage")


@app.route("/detail/<venue>", methods=["GET"])
def show_detail(venue):
    if isAdmin == False:
        return redirect("/")
    else:
        try:
            con = open_DB("base.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM Venues where name=?", (venue,))
            row = cur.fetchone()
        except Exception as e:
            print(str(e))
        try:
            cur.execute("SELECT * FROM Exits INNER JOIN Venues ON Exits.Exit=Venues.Name WHERE Exits.location=?", (venue,))
            
            line = cur.fetchall() 
            print(line)
            print(line["Name"])
            print(line["location"])
        except Exception as e:
            print(str(e))
        con.commit()
        con.close()
        print(row)
        if len(line) == 0:
            print(None)
            return render_template("venue_detail.html", data = row, NoExits = True)
        else:
            print(line)
            return render_template("venue_detail.html", data = row, links = line, NoExits = False)


@app.route("/edit/<venue>", methods = ['GET'])
def edit_venue(venue):
    if isAdmin == False:
        return redirect("/")
    else:
        try:
            con = open_DB("base.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM Venues where name=?", (venue,))
            row = cur.fetchone()
            con.commit()


        except Exception as e:
            print(str(e))
        con.close()
        return render_template("venue_edit.html", data = row)


@app.route("/update/<venue>/", methods = ['POST'])
def update_venue(venue):
    if isAdmin == False:
        return redirect("/")
    else:
        image_file_name=""
        
        if "image" in request.files:
            try:
                if "image" in request.files:
                    image_file = request.files["image"]
                    image_file_name = image_file.filename
                    if image_file_name:
                        print("imagefilename: " + image_file_name + "\n\n\n\n\n")
                        image_file.save("static/images/" + image_file_name)
            except Exception as e:
                return str(e)
        
        try:
            con = open_DB("base.db")
            con.row_factory = sqlite3.Row #name-based access to columns
            cur = con.cursor()
            if request.form["submit"] == "update" and image_file_name == "":
                cur.execute("UPDATE venues set name=?, description=?, location=? where name=?",
                    (request.form["name"], request.form["description"], request.form["location"],venue))
            elif request.form["submit"] == "update" and image_file_name != "":
                cur.execute("UPDATE venues set name=?, description=?, location=?, iamge=? where name=?",
                (request.form["name"], request.form["description"], request.form["price"], image_file_name, venue))
            elif request.form["submit"] == "delete":
                cur.execute("DELETE FROM Venues WHERE name=?",(venue,))
                cur.execute("DELETE FROM Exits WHERE location=?",(venue,))
                cur.execute("DELETE FROM Exits WHERE exit=?",(venue,))
                msg="Venue deleted"
                print(msg)
            con.commit()
            con.close()
        except Exception as e:
            print("*"+str(e))
        con.close()

        return redirect("/homepage")


@app.route("/register", methods=["GET"] )
def register():
    return render_template("register.html")


@app.route("/reg", methods=["POST","GET"])
def reg():
    if request.form["email"] != "" and request.form["psw"] != "" :
        con = open_DB("base.db")
        con.execute("INSERT INTO Admins(Username, Password) " +
                            "VALUES(?,?)",
                            (request.form["email"], request.form["psw"]))
        con.commit()
        con.close()
    return redirect("/")

@app.route("/logout")
def logout():
    global isAdmin
    isAdmin = False
    return redirect("/")

if __name__ == "__main__":
    isAdmin = False
    #app.run(host = "127.0.0.1", port = 8080, debug = True)
    app.run(debug = True)

