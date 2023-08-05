from wordpress_xmlrpc import Client
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc.methods import posts

from . import config


def post_to_wp(title, content):
    wp = Client(config.wordpress_client, config.wordpress_username, config.wordpress_password)
    post = WordPressPost()
    post.title = title
    post.content = content
    post.id = wp.call(posts.NewPost(post))

    # whoops, I forgot to publish it!
    post.post_status = 'publish'
    wp.call(posts.EditPost(post.id, post))
