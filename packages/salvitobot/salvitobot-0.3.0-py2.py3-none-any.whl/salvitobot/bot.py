from salvitobot import Bot


def main():
    bot = Bot()
    bot.get_quake(country='Peru')
    if bot.is_new_quake():
        bot.write_stories()
        # bot.post_to_wp()
        bot.tweet()


if __name__ == "__main__":
    main()
