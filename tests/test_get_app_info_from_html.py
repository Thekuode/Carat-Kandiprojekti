# These tests focus on the get_app_info_from_html function
# The function and cover various scenarios such as:
# 
# 1. When all information is present
# 2. When some information is missing 
# 3. When all information is missing
# 4. When the HTML is not in a correct format
# 5. When only parts of the information are available
#
# The tests use mock HTML to simulate the structure of real Google Play Store pages.
# The expected output for each test is compared with the actual output returned 
# by the function and if they match, the test is considered successful

import pytest
from play_store_fetcher import get_app_info_from_html

def test_get_app_info_from_html() -> None:
    # test when all the requested information is present
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated 3.7 stars out of five stars">3.7
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">1.58K reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">100K+</div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <img src="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w48-h16" srcset="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w96-h32 2x" class="T75of xGa6dd" alt="Content rating" itemprop="image" data-atf="true" data-iml="188">
                            </div>
                            <div class="g1rdde">
                                <span itemprop="contentRating">
                                    <span>PEGI 3</span>
                                </span>
                                <div jscontroller="kJXwXb" jsaction="click:CnOdef" class="MKV5ee" role="button" tabindex="0" aria-label="More info about this content rating">
                                    <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="xg1aie">Last Updated: Jan 1, 2025</div>
        </body>
    </html>
    '''
    expected = ("3.7", "100K+", "1.58K", "Jan 1, 2025")
    result = get_app_info_from_html(mock_html)
    assert result == expected

def test_get_app_info_from_html_missing_info() -> None:
    # test when last updated info is missing
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated 3.7 stars out of five stars">3.7
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">1.58K reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">100K+</div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <img src="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w48-h16" srcset="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w96-h32 2x" class="T75of xGa6dd" alt="Content rating" itemprop="image" data-atf="true" data-iml="188">
                            </div>
                            <div class="g1rdde">
                                <span itemprop="contentRating">
                                    <span>PEGI 3</span>
                                </span>
                                <div jscontroller="kJXwXb" jsaction="click:CnOdef" class="MKV5ee" role="button" tabindex="0" aria-label="More info about this content rating">
                                    <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''
    expected = ("3.7", "100K+", "1.58K", "Not Found")
    result = get_app_info_from_html(mock_html)
    assert result == expected

def test_get_app_info_from_html_no_info() -> None:
    # test when all info is missing
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated 3.7 stars out of five stars">
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O"></div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <img src="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w48-h16" srcset="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w96-h32 2x" class="T75of xGa6dd" alt="Content rating" itemprop="image" data-atf="true" data-iml="188">
                            </div>
                            <div class="g1rdde">
                                <span itemprop="contentRating">
                                    <span>PEGI 3</span>
                                </span>
                                <div jscontroller="kJXwXb" jsaction="click:CnOdef" class="MKV5ee" role="button" tabindex="0" aria-label="More info about this content rating">
                                    <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="xg1aie"></div>
        </body>
    </html>
    '''
    expected = ("Not Found", "Not Found", "Not Found", "Not Found")
    result = get_app_info_from_html(mock_html)
    assert result == expected

def test_get_app_info_from_html_incomplete_info() -> None:
    # test when rating info is missing
    mock_html = '''
    <html>
        <body>

            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                            </div>
                        </div>
                        <div class="g1rdde">100K+ reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">1M+</div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <img src="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w48-h16" srcset="https://play-lh.googleusercontent.com/f8B0enUmZD3qSV7UvP1aFSF5nQcAE_PpEJaXsIrfPMXU_D64BmVJC138JudhaYBkamCGbl_F3wXwfi0wJg=w96-h32 2x" class="T75of xGa6dd" alt="Content rating" itemprop="image" data-atf="true" data-iml="188">
                            </div>
                            <div class="g1rdde">
                                <span itemprop="contentRating">
                                    <span>PEGI 3</span>
                                </span>
                                <div jscontroller="kJXwXb" jsaction="click:CnOdef" class="MKV5ee" role="button" tabindex="0" aria-label="More info about this content rating">
                                    <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="xg1aie">Last Updated: Jan 1, 2025</div>
        </body>
    </html>
    '''
    expected = ("Not Found", "1M+", "100K+",  "Jan 1, 2025")
    result = get_app_info_from_html(mock_html)
    assert result == expected

def test_get_app_info_from_html_invalid_format() -> None:
    # test when the HTML format is invalid or unexpected
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">Invalid format</div>
        </body>
    </html>
    '''
    expected = ("Not Found", "Not Found", "Not Found", "Not Found")
    result = get_app_info_from_html(mock_html)
    assert result == expected

def test_get_app_info_from_html_rating_only() -> None:
    # test when only rating is provided in the HTML
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated 4.5 stars out of five stars">4.5
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''
    expected = ("4.5", "Not Found", "Not Found", "Not Found")
    result = get_app_info_from_html(mock_html)
    assert result == expected
















