def fetch_articles():

    articles = []

    categories = get_categories()


    for category in categories:


        print(
            "[LIST]",
            category
        )


        soup = get_soup(
            category
        )



        for a in soup.find_all(
            "a",
            href=True
        ):


            url = urljoin(
                category,
                a["href"]
            ).split("?")[0]



            # ★記事だけ
            if "/my/uoplus/detail/c/" not in url:

                continue



            # 固定除外

            if any(x in url for x in [
                "/detail/c/mail/",
            ]):

                continue




            title = a.get_text(
                " ",
                strip=True
            )


            if not title:

                title = "UNITED ONLINE PLUS"



            articles.append(
                {
                    "url": url,
                    "title": title
                }
            )



    result = []

    exists = set()


    for article in articles:


        if article["url"] in exists:

            continue


        exists.add(
            article["url"]
        )

        result.append(article)



    print(
        "[ARTICLES]",
        len(result)
    )

    print(
        result[:10]
    )


    return result
