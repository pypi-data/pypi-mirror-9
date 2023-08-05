import datetime
import os

from slugify import slugify
from wordpress_xmlrpc import Client
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc.compat import xmlrpc_client

from . import config
from .exceptions import WordPressNotConfigured


def post_to_wp(title, content, datetime_local):
    """

    :param title: Title for post, used to guess post URL
    :param content: Body for post
    :param datetime_local: local time of earthquake, assumed to be the sames of
           WordPress instalation. Used to guess post URL
    :return: post_url
    """
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

    # set to the path to your file
    filename = os.path.join(config.base_folder, 'img', 'salvitobot.png')

    # prepare metadata
    data = {
        'name': 'salvitobot.png',
        'type': 'image/png',  # mimetype
    }

    # read the binary file and let the XMLRPC library encode it into base64
    with open(filename, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())

    response = wp.call(media.UploadFile(data))
    # response == {
    #       'id': 6,
    #       'file': 'picture.jpg'
    #       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
    #       'type': 'image/jpeg',
    # }
    attachment_id = response['id']

    post = WordPressPost()
    post.title = title
    post.content = content
    post.id = wp.call(posts.NewPost(post))

    post.terms_names = {
        'post_tag': ['salvitobot', 'temblor', 'sismo'],
        'category': ['noticias']
    }
    post.thumbnail = attachment_id
    # whoops, I forgot to publish it!
    post.post_status = 'publish'
    wp.call(posts.EditPost(post.id, post))

    # return post url based on config wp_client and datetime_local
    return make_url(title, datetime_local)


def make_url(post_title, datetime_local):
    date_str = datetime.datetime.strftime(datetime_local, '%Y/%m/%d/')

    post_url = config.wordpress_client.replace('xmlrpc.php', '')
    post_url += date_str
    post_url += slugify(post_title, max_length=200) + '/'
    return post_url
