# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

from datetime import datetime
from exceptions import Exception
import re
import requests
from bs4 import BeautifulSoup


class RateBeer(object):
    """
    Makes getting information about beers and breweries from RateBeer.com easy.

    >>> summit_search = RateBeer().search("summit extra pale ale")

    A utility for searching RateBeer.com, finding information about beers,
    breweries, and reviews. The nature of web scraping means that this package
    is offered in perpetual beta.

    Requires BeautifulSoup4, Requests, and lxml. See
    https://github.com/alilja/ratebeer for the full README.

    """
    _BASE_URL = "http://www.ratebeer.com"

    class PageNotFound(Exception):
        """Returns the URL of the page not found."""
        pass

    class AliasedBeer(Exception):
        """Returns the old and new urls for an aliased beer."""
        def __init__(self, oldurl, newurl):
            self.oldurl = oldurl
            self.newurl = newurl

    def _get_soup(self, url):
        req = requests.get(RateBeer._BASE_URL + url, allow_redirects=True)
        if "ratebeer robot oops" in req.text.lower():
            raise RateBeer.PageNotFound(url)
        return BeautifulSoup(req.text, "lxml")

    def search(self, query):
        """Returns a list of beers and breweries that matched the search query.

        Args:
            query (string): The text of the search.

        Returns:
            A dictionary containing two lists, ``breweries`` and ``beers``.
            Each list contains a dictionary of attributes of that brewery or
            beer.
        """
        r = requests.post(RateBeer._BASE_URL + "/findbeer.asp",
                          data={"BeerName": query})
        soup = BeautifulSoup(r.text, "lxml")
        soup_results = soup.find_all('table', {'class': 'results'})
        output = {"breweries": [], "beers": []}

        # Locate rows that contain the brewery and beer info
        for index, val in enumerate(soup.find_all("h1")):
            if "brewers" in val:
                # find brewery information
                soup_breweries = soup_results[index - 1].find_all('tr')
                for row in soup_breweries:
                    location = row.find('td', {'align': 'right'})

                    output['breweries'].append({
                        "name": row.a.text,
                        "url": row.a.get('href'),
                        "id": re.search(r"/(?P<id>\d*)/", row.a.get('href')).group('id'),
                        "location": location.text.strip(),
                    })

            elif "beers" in val:
                # find beer information
                if not soup.find_all(text="0 beers"):
                    soup_beer_rows = iter(soup_results[index - 1].find_all('tr'))
                    next(soup_beer_rows)
                    for row in soup_beer_rows:
                        link = row.find('td', 'results').a
                        align_right = row.find_all("td", {'align': 'right'})

                        output['beers'].append({
                            "name": link.text,
                            "url": link.get('href'),
                            "id": re.search(r"/(?P<id>\d*)/", link.get('href')).group('id'),
                            "rating": align_right[-2].text.strip(),
                            "num_ratings": align_right[-1].text,
                        })
        return output

    def beer(self, url):
        """Returns information about a specific beer.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/beer/deschutes-inversion-ipa/55610/"

        Returns:
            A dictionary of attributes about that beer."""
        soup = self._get_soup(url)
        output = {}

        # check for 404s
        try:
            s_contents_rows = soup.find('div', id='container').find('table').find_all('tr')
        except AttributeError:
            raise RateBeer.PageNotFound(url)
        # ratebeer pages don't actually 404, they just send you to this weird
        # "beer reference" page but the url doesn't actually change, it just
        # seems like it's all getting done server side -- so we have to look
        # for the contents h1 to see if we're looking at the beer reference or
        # not
        if "beer reference" in s_contents_rows[0].find_all('td')[1].h1.contents:
            raise RateBeer.PageNotFound(url)

        if "Also known as " in s_contents_rows[1].find_all('td')[1].div.div.contents:
            raise RateBeer.AliasedBeer(url, s_contents_rows[1].find_all('td')[1].div.div.a['href'])

        brew_url = soup.find('link', rel='canonical')['href'].replace(RateBeer._BASE_URL, '')
        brew_info_row = s_contents_rows[1].find_all('td')[1].div.small
        brew_info = brew_info_row.text.split(u'\xa0\xa0')
        brew_info = [s.split(': ') for s in brew_info]
        keywords = {
            "RATINGS": "num_ratings",
            "MEAN": "mean",
            "WEIGHTED AVG": "weighted_avg",
            "SEASONAL": "seasonal",
            "CALORIES": "calories",
            "ABV": "abv",
            "IBU": "ibu",
        }
        for meta_name, meta_data in brew_info:
            for keyword in keywords:
                if keyword in meta_name and meta_data:
                    if keyword == "MEAN":
                        meta_data = meta_data[:meta_data.find("/")]
                    if keyword == "ABV":
                        meta_data = meta_data[:-1]

                    try:
                        meta_data = float(meta_data)
                    except ValueError:
                        pass

                    output[keywords[keyword]] = meta_data
                    break

        info = s_contents_rows[1].tr.find_all('td')

        brewery_info = info[1].find('div').contents
        brewery = brewery_info[0].findAll('a')[0]
        brewed_at = None
        if 'Brewed at' in brewery_info[0].text:
            brewed_at = brewery_info[0].findAll('a')[1]

        style = brewery_info[3]
        description = s_contents_rows[1].find_all('td')[1].find(
            'div', style=(
                'border: 1px solid #e0e0e0; background: #fff; '
                'padding: 14px; color: #777;'
            )
        )

        name = s_contents_rows[0].find_all('td')[1].h1
        ratings = info[0].findAll('div')
        if len(ratings) > 1:
            overall_rating = ratings[1].findAll('span')
            style_rating = ratings[3].findAll('span')
        else:
            overall_rating = None
            style_rating = None

        output['name'] = name.text.strip()
        output['url'] = brew_url
        if overall_rating and overall_rating[1].text != 'n/a':
            output['overall_rating'] = int(overall_rating[1].text)
        if style_rating and style_rating[0].text != 'n/a':
            output['style_rating'] = int(style_rating[0].text)
        if brewery:
            output['brewery'] = brewery.text.strip()
            output['brewery_url'] = brewery.get('href')
        if brewed_at:
            output['brewed_at'] = brewed_at.text.strip()
            output['brewed_at_url'] = brewed_at.get('href')
        if style:
            output['style'] = style.text.strip()
        if 'No commercial description' not in description.text:
            _ = [s.extract() for s in description('small')]
            output['description'] = ' '.join([s for s in description.strings]).strip()
        return output

    def reviews(self, url, review_order="most recent"):
        """Returns reviews for a specific beer.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/beer/deschutes-inversion-ipa/55610/"
            review_order (string): How to sort reviews. Three inputs:
                most recent: Newer reviews appear earlier.
                top raters: RateBeer.com top raters appear earlier.
                highest score: Reviews with the highest overall score appear
                earlier.

        Returns:
            A generator of dictionaries, containing the information about the review.
        """

        review_order = review_order.lower()
        url_codes = {
            "most recent": 1,
            "top raters": 2,
            "highest score": 3
        }
        url_flag = url_codes.get(review_order)
        if url_flag is None:
            raise ValueError("Invalid ``review_order``.")

        page_number = 1
        while True:
            complete_url = "{0}{1}/{2}/".format(url, url_flag, page_number)
            soup = self._get_soup(complete_url)
            content = soup.find('table', style='padding: 10px;').tr.td
            reviews = content.find_all('div', style='padding: 0px 0px 0px 0px;')

            if len(reviews) < 1:
                raise StopIteration

            for review in reviews:
                rating_details = review.find_all('div')
                # gets every second entry in a list
                individual_ratings = zip(*[iter(review.find('strong').find_all(["big", "small"]))]*2)

                details = {}
                details.update(dict([(
                    label.text.lower().strip().encode("ascii", "ignore"),
                    rating.text,
                ) for (label, rating) in individual_ratings]))
                userinfo = review.next_sibling

                details['rating'] = float(rating_details[1].text)
                details['user_name'] = re.findall(r'(.*?)\xa0\(\d*?\)', userinfo.a.text)[0]
                details['user_location'] = re.findall(r'-\s(.*?)\s-', userinfo.a.next_sibling)[0]
                details['date'] = re.findall(r'-\s.*?\s-\s(.*)', userinfo.a.next_sibling)[0]
                details['date'] = datetime.strptime(details['date'].strip(), '%b %d, %Y').date()
                details['text'] = userinfo.next_sibling.next_sibling.text.strip()
                yield details

            page_number += 1

    def brewery(self, url, include_beers=True):
        """Returns information about a specific brewery.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/brewers/new-belgium-brewing-company/77/"

        Returns:
            A dictionary of attributes about that brewery."""
        def _find_span(search_soup, item_prop):
            output = search_soup.find('span', attrs={'itemprop': item_prop})
            output = output.text if output else None
            return output

        soup = self._get_soup(url)
        try:
            s_contents = soup.find('div', id='container').find('table').find_all('tr')[0].find_all('td')
        except AttributeError:
            raise RateBeer.PageNotFound(url)

        output = {
            'name': s_contents[8].h1.text,
            'type': re.search(r"Type: +(?P<type>[^ ]+)",
                              s_contents[8].find_all('span', 'beerfoot')[1].text).group('type'),
            'street': _find_span(s_contents[0], 'streetAddress'),
            'city': _find_span(s_contents[0], 'addressLocality'),
            'state': _find_span(s_contents[0], 'addressRegion'),
            'country': _find_span(s_contents[0], 'addressCountry'),
            'postal_code': _find_span(s_contents[0], 'postalCode'),
        }

        if include_beers:
            output['beers'] = []
            s_beer_trs = iter(s_contents[8].find('table', 'maintable nohover').find_all('tr'))
            next(s_beer_trs)
            for row in s_beer_trs:
                if len(row.find_all('td')) > 1:
                    beer = {
                        'name': row.a.text,
                        'url': row.a.get('href'),
                        'id': re.search(r"/(?P<id>\d*)/", row.a.get('href')).group('id'),
                        'rating': row.find_all('td')[4].text.strip(),
                        'num_ratings': row.find_all('td')[6].text.strip(),
                    }
                    output['beers'].append(beer)
        return output

    def beer_style_list(self):
        """Returns the list of beer styles from the beer styles page.

        Returns:
            A dictionary, with beer styles for keys and urls for values.
        """
        styles = {}

        soup = self._get_soup("/beerstyles/")
        columns = soup.find_all('table')[2].find_all('td')
        for column in columns:
            lines = [li for li in column.find_all('li')]
            for line in lines:
                styles[line.text] = line.a.get('href')
        return styles

    def beer_style(self, url, sort_type="overall"):
        """Get all the beers from a specific beer style page.

        Args:
            url (string): The specific url of the beer style. Looks like:
                "/beerstyles/abbey-dubbel/71/"
            sort_type (string): The sorting of the results. "overall" returns
                the highest- rated beers, while "trending" returns the newest
                and trending ones.

        Returns:
            A list of dictionaries containing the beers.
        """
        sort_type = sort_type.lower()
        url_codes = {"overall": 0, "trending": 1}
        sort_flag = url_codes.get(sort_type)
        if sort_flag is None:
            raise ValueError("Invalid ``sort_type``.")
        style_id = re.search(r"/(?P<id>\d*)/", url).group('id')

        req = requests.post(
            RateBeer._BASE_URL +
            (
                "/ajax/top-beer-by-style.asp?style={0}&sort={1}"
                "&order=0&min=10&max=9999&retired=0&new=0&mine=0&"
            )
            .format(style_id, sort_flag),
            allow_redirects=True
        )
        soup = BeautifulSoup(req.text, "lxml")
        rows = iter(soup.table.find_all('tr'))
        next(rows)

        output = []
        for row in rows:
            data = row.find_all('td')
            output.append({
                'name': data[1].text,
                'url': data[1].a.get('href'),
                'rating': data[4].text
            })
        return output
