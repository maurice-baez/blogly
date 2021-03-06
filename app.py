"""Blogly application."""

# from tabnanny import process_tokens
from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post, Tag, PostTag, DEFAULT_IMAGE_URL
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret-key'

debug = DebugToolbarExtension(app)



connect_db(app)
db.create_all()


@app.get("/")
def redirect_to_users():
    """ Redirect to display users """
    return redirect("/users")


@app.get("/users")
def show_users():
    """ Show all current users """

    users = User.query.all()

    return render_template("user_listing.html", users=users)


@app.get("/users/new")
def show_new_user_form():
    """ Display new user form """

    return render_template("new_user_form.html")


@app.post("/users/new")
def process_and_add_new_user():
    """ Process form and add new user to database. Redirect to users list """

    first_name = request.form.get("first-name")
    last_name = request.form.get("last-name")
    image_url = request.form.get("image-url")

    new_user = User(first_name = first_name, last_name = last_name, image_url = image_url)

    # Add new object to session, so they'll persist
    db.session.add(new_user)

    db.session.commit()

    flash('User created!')

    return redirect("/users")


@app.get("/users/<int:user_id>")
def show_user_details(user_id):
    """ Show profile page for user """

    # grab user id object
    user = User.query.get_or_404(user_id)
    posts = user.posts

    return render_template("user_detail_page.html", user = user, posts=posts)


@app.get("/users/<int:user_id>/edit")
def show_user_edit_page(user_id):
    """ Show edit page for user """

    user = User.query.get_or_404(user_id)

    return render_template("user_edit_page.html", user = user)


@app.post("/users/<int:user_id>/edit")
def process_user_edit(user_id):
    """ Update database with user edits and return user to user's profile """

    first_name = request.form.get("first-name-edit")
    last_name = request.form.get("last-name-edit")
    image_url = request.form.get("image-url-edit") or DEFAULT_IMAGE_URL

    user = User.query.get_or_404(user_id)

    user.first_name = first_name
    user.last_name = last_name

    user.image_url = image_url

    db.session.add(user)
    db.session.commit()

    flash("Profile successfully updated")

    return redirect(f"/users/{user_id}")


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """ Delete user and redirect to users list """

    user = User.query.get_or_404(user_id)

    for post in user.posts:
        db.session.delete(post)

    db.session.delete(user)
    db.session.commit()

    flash("User successfully deleted")

    return redirect("/users")



# BLOG POST ROUTES

@app.get("/users/<int:user_id>/posts/new")
def show_new_post_form(user_id):
    """ Show new post form for user"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template("new_post_form.html", user=user, tags=tags)


@app.post("/users/<int:user_id>/posts/new")
def process_and_add_new_post(user_id):
    """ Process new post form, add post to database, redirect to user detail page """

    title = request.form.get("title")
    content = request.form.get("content")

    tag_names = request.form.getlist("tag-name")

    new_post = Post(title = title, content=content, user_id=user_id)

    db.session.add(new_post)
    db.session.commit()

    for tag_name in tag_names:

        tag = Tag.query.filter_by(name=tag_name).one()

        posttag = PostTag(post_id=new_post.id ,tag_id=tag.id)
        db.session.add(posttag)

    db.session.commit()

    flash("Post successfully added")

    return redirect(f"/users/{user_id}")

@app.get("/posts/<int:post_id>")
def show_post_detail(post_id):
    """ Show post detail """

    post = Post.query.get_or_404(post_id)

    return render_template("post_detail_page.html", post=post)


@app.get("/posts/<int:post_id>/edit")
def show_edit_post_form(post_id):
    """ Show form to edit post """

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()


    return render_template("post_edit_page.html", post=post, tags=tags)


@app.post("/posts/<int:post_id>/edit")
def process_post_edit(post_id):
    """ Process change data in post, update data base, redirect to post view"""

    new_title = request.form.get("title-edit")
    new_content = request.form.get("content-edit")

    tag_names = request.form.getlist("tag-name")

    post = Post.query.get_or_404(post_id)

    post.title = new_title
    post.content = new_content

    db.session.add(post)
    db.session.commit()


    posttags = PostTag.query.filter(PostTag.post_id == post.id)

    for posttag in posttags:
        db.session.delete(posttag)

    db.session.commit()

    for tag_name in tag_names:

        tag = Tag.query.filter_by(name=tag_name).one()

        posttag = PostTag(post_id=post.id ,tag_id=tag.id)
        db.session.add(posttag)

    db.session.commit()

    flash("Post changes saved")

    return redirect(f"/posts/{post_id}")

@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id):
    """ Delete post from database """

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    flash("Post removed")

    return redirect(f"/users/{post.user_id}")



# TAG ROUTES

@app.get("/tags")
def show_tags():
    """Show tag list"""

    tags = Tag.query.all()
    return render_template("tags_list.html", tags=tags)

@app.get("/tags/<int:tag_id>")
def show_tag_details(tag_id):
    """ Show detail page for a tag """

    tag = Tag.query.get_or_404(tag_id)

    return render_template("tag_details.html", tag=tag)

@app.get("/tags/new")
def show_new_tag_form():
    """ Show new tag form"""
    return render_template("new_tag_form.html")

@app.post("/tags/new")
def process_new_tag_submit():
    """ Process adding of new tag. Redirect to tag list"""
    name = request.form.get("tag-name")
    tag = Tag(name = name)

    db.session.add(tag)
    db.session.commit()
    return redirect("/tags")

@app.get("/tags/<int:tag_id>/edit")
def show_tag_edit_form(tag_id):
    """ Show tag editing form """

    tag = Tag.query.get_or_404(tag_id)

    return render_template("edit_tag.html", tag=tag)


@app.post("/tags/<int:tag_id>/edit")
def process_tag_edit(tag_id):
    """ process tag edits and redirect to tag detail page """

    tag = Tag.query.get_or_404(tag_id)
    tag_name = request.form.get("tag-name-edit")

    tag.name = tag_name

    db.session.add(tag)
    db.session.commit()

    return redirect(f"/tags/{tag_id}")

@app.post("/tags/<int:tag_id>/delete")
def delete_tag(tag_id):
    """ Delete a tag """

    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")
