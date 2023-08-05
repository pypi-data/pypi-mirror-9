from wordpress_xmlrpc import Client
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc.methods import posts

from . import config
from .exceptions import WordPressNotConfigured


def post_to_wp(title, content):
    msg = "\nYou need to set up your WordPress credentials: \n" \
          "Use:\n" \
          "    salvitobot.config.wordpress_client = 'https://mydomain.wordpress.com/xmlrpc.php'\n" \
          "    salvitobot.config.wordpress_username = 'yourusername'\n" \
          "    salvitobot.config.wordpress_password = 'yourpassword'\n"

    if config.wordpress_client == '':
        raise WordPressNotConfigured(msg)
    if config.wordpress_username == '':
        raise WordPressNotConfigured(msg)
    if config.wordpress_password == '':
        raise WordPressNotConfigured(msg)

    wp = Client(config.wordpress_client, config.wordpress_username, config.wordpress_password)
    post = WordPressPost()
    post.title = title
    post.content = content
    post.id = wp.call(posts.NewPost(post))

    # whoops, I forgot to publish it!
    post.post_status = 'publish'
    wp.call(posts.EditPost(post.id, post))
