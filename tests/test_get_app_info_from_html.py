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

#Tests trough the possible value types for each field
COMPLETE_VALUE_TEST_BATTERY = [
    #Rating tests
    ("Review is integer", "3", "100", "1000", "Jan 1, 2025", ("3", "1000", "100", "Jan 01, 2025")),
    ("Review is floating point .1", "3.1", "100", "1000", "Jan 1, 2025", ("3.1", "1000", "100", "Jan 01, 2025")),
    ("Review is floating point .12", "3.12", "100", "1000", "Jan 1, 2025", ("3.12", "1000", "100", "Jan 01, 2025")),
    ("Review is floating point .123", "3.123", "100", "1000", "Jan 1, 2025", ("3.123", "1000", "100", "Jan 01, 2025")),
    #Reviw count tests, integer
    ("Review count is integer", "3", "100", "1000", "Jan 1, 2025", ("3", "1000", "100", "Jan 01, 2025")),
    ("Review count is integer", "3", "100+", "1000", "Jan 1, 2025", ("3", "1000", "100+", "Jan 01, 2025")),
    ("Review count is integer postfix K","3", "100K", "1000", "Jan 1, 2025", ("3", "1000", "100K", "Jan 01, 2025")),
    ("Review count is integer postfix M","3", "100M", "1000", "Jan 1, 2025", ("3", "1000", "100M", "Jan 01, 2025")),
    ("Review count is integer postfix B","3", "100B", "1000", "Jan 1, 2025", ("3", "1000", "100B", "Jan 01, 2025")),
    ("Review count is integer postfix K+","3", "100K+", "1000", "Jan 1, 2025", ("3", "1000", "100K+", "Jan 01, 2025")),
    ("Review count is integer postfix M+","3", "100M+", "1000", "Jan 1, 2025", ("3", "1000", "100M+", "Jan 01, 2025")),
    ("Review count is integer postfix B+","3", "100B+", "1000", "Jan 1, 2025", ("3", "1000", "100B+", "Jan 01, 2025")),
    #Reviw count tests, floating point
    ("Review count is float postfix K","3", "1.58K", "1000", "Jan 1, 2025", ("3", "1000", "1.58K", "Jan 01, 2025")),
    ("Review count is float postfix M","3", "1.58M", "1000", "Jan 1, 2025", ("3", "1000", "1.58M", "Jan 01, 2025")),
    ("Review count is float postfix B","3", "1.58B", "1000", "Jan 1, 2025", ("3", "1000", "1.58B", "Jan 01, 2025")),
    ("Review count is float postfix K+","3", "1.58K+", "1000", "Jan 1, 2025", ("3", "1000", "1.58K+", "Jan 01, 2025")),
    ("Review count is float postfix M+","3", "1.58M+", "1000", "Jan 1, 2025", ("3", "1000", "1.58M+", "Jan 01, 2025")),
    ("Review count is float postfix B+","3", "1.58B+", "1000", "Jan 1, 2025", ("3", "1000", "1.58B+", "Jan 01, 2025")),
    #Download count tests, integer
    ("Download count is integer", "3", "100", "1000", "Jan 1, 2025", ("3", "1000", "100", "Jan 01, 2025")),
    ("Download count is integer", "3", "100", "1000+", "Jan 1, 2025", ("3", "1000+", "100", "Jan 01, 2025")),
    ("Download count is integer postfix K","3", "100K", "1000K", "Jan 1, 2025", ("3", "1000K", "100K", "Jan 01, 2025")),
    ("Download count is integer postfix M","3", "100M", "1000M", "Jan 1, 2025", ("3", "1000M", "100M", "Jan 01, 2025")),
    ("Download count is integer postfix B","3", "100B", "1000B", "Jan 1, 2025", ("3", "1000B", "100B", "Jan 01, 2025")),
    ("Download count is integer postfix K+","3", "100K+", "1000K+", "Jan 1, 2025", ("3", "1000K+", "100K+", "Jan 01, 2025")),
    ("Download count is integer postfix M+","3", "100M+", "1000M+", "Jan 1, 2025", ("3", "1000M+", "100M+", "Jan 01, 2025")),
    ("Download count is integer postfix B+","3", "100B+", "1000B+", "Jan 1, 2025", ("3", "1000B+", "100B+", "Jan 01, 2025")),
    #Download count tests, floating point
    ("Download count is float postfix K","3", "1.58K", "1.58K", "Jan 1, 2025", ("3", "1.58K", "1.58K", "Jan 01, 2025")),
    ("Download count is float postfix M","3", "1.58M", "1.58M", "Jan 1, 2025", ("3", "1.58M", "1.58M", "Jan 01, 2025")),
    ("Download count is float postfix B","3", "1.58B", "1.58B", "Jan 1, 2025", ("3", "1.58B", "1.58B", "Jan 01, 2025")),
    ("Download count is float postfix K+","3", "1.58K+", "1.58K+", "Jan 1, 2025", ("3", "1.58K+", "1.58K+", "Jan 01, 2025")),
    ("Download count is float postfix M+","3", "1.58M+", "1.58M+", "Jan 1, 2025", ("3", "1.58M+", "1.58M+", "Jan 01, 2025")),
    ("Download count is float postfix B+","3", "1.58B+", "1.58B+", "Jan 1, 2025", ("3", "1.58B+", "1.58B+", "Jan 01, 2025")),
    #Month Date, Year
    #Months
    ("MD,Y: Month is Jan","3", "1.58K", "1.58K", "Jan 1, 2025", ("3", "1.58K", "1.58K", "Jan 01, 2025")),
    ("MD,Y: Month is Feb","3", "1.58M", "1.58M", "Feb 1, 2025", ("3", "1.58M", "1.58M", "Feb 01, 2025")),
    ("MD,Y: Month is Mar","3", "1.58B", "1.58B", "Mar 1, 2025", ("3", "1.58B", "1.58B", "Mar 01, 2025")),
    ("MD,Y: Month is Apr","3", "1.58K+", "1.58K+", "Apr 1, 2025", ("3", "1.58K+", "1.58K+", "Apr 01, 2025")),
    ("MD,Y: Month is May","3", "1.58M+", "1.58M+", "May 1, 2025", ("3", "1.58M+", "1.58M+", "May 01, 2025")),
    ("MD,Y: Month is Jun","3", "1.58B+", "1.58B+", "Jun 1, 2025", ("3", "1.58B+", "1.58B+", "Jun 01, 2025")),
    ("MD,Y: Month is Jul","3", "1.58K", "1.58K", "Jul 1, 2025", ("3", "1.58K", "1.58K", "Jul 01, 2025")),
    ("MD,Y: Month is Aug","3", "1.58M", "1.58M", "Aug 1, 2025", ("3", "1.58M", "1.58M", "Aug 01, 2025")),
    ("MD,Y: Month is Sep","3", "1.58B", "1.58B", "Sep 1, 2025", ("3", "1.58B", "1.58B", "Sep 01, 2025")),
    ("MD,Y: Month is Oct","3", "1.58K+", "1.58K+", "Oct 1, 2025", ("3", "1.58K+", "1.58K+", "Oct 01, 2025")),
    ("MD,Y: Month is Nov","3", "1.58M+", "1.58M+", "Nov 1, 2025", ("3", "1.58M+", "1.58M+", "Nov 01, 2025")),
    ("MD,Y: Month is Dec","3", "1.58B+", "1.58B+", "Dec 1, 2025", ("3", "1.58B+", "1.58B+", "Dec 01, 2025")),
    #Date is 1,10,20,30
    ("MD,Y: Date is 1","3", "1.58K", "1.58K", "Jan 1, 2025", ("3", "1.58K", "1.58K", "Jan 01, 2025")),
    ("MD,Y: Date is 10","3", "1.58M", "1.58M", "Feb 10, 2025", ("3", "1.58M", "1.58M", "Feb 10, 2025")),
    ("MD,Y: Date is 20","3", "1.58B", "1.58B", "Mar 20, 2025", ("3", "1.58B", "1.58B", "Mar 20, 2025")),
    ("MD,Y: Date is 30","3", "1.58B", "1.58B", "Mar 30, 2025", ("3", "1.58B", "1.58B", "Mar 30, 2025")),
    #Year is 1900, 2000, 2010, 2020, 2030, 2040
    ("MD,Y: Year is 1900","3", "1.58K", "1.58K", "Jan 1, 1900", ("3", "1.58K", "1.58K", "Jan 01, 1900")),
    ("MD,Y: Year is 2000","3", "1.58M", "1.58M", "Feb 10, 2000", ("3", "1.58M", "1.58M", "Feb 10, 2000")),
    ("MD,Y: Year is 2010","3", "1.58B", "1.58B", "Mar 20, 2010", ("3", "1.58B", "1.58B", "Mar 20, 2010")),
    ("MD,Y: Year is 2020","3", "1.58B", "1.58B", "Mar 30, 2020", ("3", "1.58B", "1.58B", "Mar 30, 2020")),
    ("MD,Y: Year is 2030","3", "1.58B", "1.58B", "Mar 30, 2030", ("3", "1.58B", "1.58B", "Mar 30, 2030")),
    ("MD,Y: Year is 2040","3", "1.58B", "1.58B", "Mar 30, 2040", ("3", "1.58B", "1.58B", "Mar 30, 2040")),

    #Date Month Year
    #Months
    ("DMY: Month is Jan","3", "1.58K", "1.58K", "1 Jan 2025", ("3", "1.58K", "1.58K", "Jan 01, 2025")),
    ("DMY: Month is Feb","3", "1.58M", "1.58M", "1 Feb 2025", ("3", "1.58M", "1.58M", "Feb 01, 2025")),
    ("DMY: Month is Mar","3", "1.58B", "1.58B", "1 Mar 2025", ("3", "1.58B", "1.58B", "Mar 01, 2025")),
    ("DMY: Month is Apr","3", "1.58K+", "1.58K+", "1 Apr 2025", ("3", "1.58K+", "1.58K+", "Apr 01, 2025")),
    ("DMY: Month is May","3", "1.58M+", "1.58M+", "1 May 2025", ("3", "1.58M+", "1.58M+", "May 01, 2025")),
    ("DMY: Month is Jun","3", "1.58B+", "1.58B+", "1 Jun 2025", ("3", "1.58B+", "1.58B+", "Jun 01, 2025")),
    ("DMY: Month is Jul","3", "1.58K", "1.58K", "1 Jul 2025", ("3", "1.58K", "1.58K", "Jul 01, 2025")),
    ("DMY: Month is Aug","3", "1.58M", "1.58M", "1 Aug 2025", ("3", "1.58M", "1.58M", "Aug 01, 2025")),
    ("DMY: Month is Sep","3", "1.58B", "1.58B", "1 Sep 2025", ("3", "1.58B", "1.58B", "Sep 01, 2025")),
    ("DMY: Month is Oct","3", "1.58K+", "1.58K+", "1 Oct 2025", ("3", "1.58K+", "1.58K+", "Oct 01, 2025")),
    ("DMY: Month is Nov","3", "1.58M+", "1.58M+", "1 Nov 2025", ("3", "1.58M+", "1.58M+", "Nov 01, 2025")),
    ("DMY: Month is Dec","3", "1.58B+", "1.58B+", "1 Dec 2025", ("3", "1.58B+", "1.58B+", "Dec 01, 2025")),
    #Date is 1,10,20,30
    ("DMY: Date is 1","3", "1.58K", "1.58K", "1 Jan 2025", ("3", "1.58K", "1.58K", "Jan 01, 2025")),
    ("DMY: Date is 10","3", "1.58M", "1.58M", "10 Feb 2025", ("3", "1.58M", "1.58M", "Feb 10, 2025")),
    ("DMY: Date is 20","3", "1.58B", "1.58B", "20 Mar 2025", ("3", "1.58B", "1.58B", "Mar 20, 2025")),
    ("DMY: Date is 30","3", "1.58B", "1.58B", "30 Mar 2025", ("3", "1.58B", "1.58B", "Mar 30, 2025")),
    #Year is 1900, 2000, 2010, 2020, 2030, 2040
    ("DMY: Year is 1900","3", "1.58K", "1.58K", "1 Jan 1900", ("3", "1.58K", "1.58K", "Jan 01, 1900")),
    ("DMY: Year is 2000","3", "1.58M", "1.58M", "10 Feb 2000", ("3", "1.58M", "1.58M", "Feb 10, 2000")),
    ("DMY: Year is 2010","3", "1.58B", "1.58B", "20 Mar 2010", ("3", "1.58B", "1.58B", "Mar 20, 2010")),
    ("DMY: Year is 2020","3", "1.58B", "1.58B", "30 Mar 2020", ("3", "1.58B", "1.58B", "Mar 30, 2020")),
    ("DMY: Year is 2030","3", "1.58B", "1.58B", "30 Mar 2030", ("3", "1.58B", "1.58B", "Mar 30, 2030")),
    ("DMY: Year is 2040","3", "1.58B", "1.58B", "30 Mar 2040", ("3", "1.58B", "1.58B", "Mar 30, 2040")),
] 

#Test inputs as tuple[str, str, str, str, str]
@pytest.mark.parametrize("test_purpose, rating_value, review_count, download_count, last_updated, expected", COMPLETE_VALUE_TEST_BATTERY)
def test_get_app_info_from_html(test_purpose: str, rating_value: str, review_count: str, download_count:str, last_updated: str, expected: tuple) -> None:
    # test when all the requested information is present
    mock_html = f'''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated {rating_value} stars out of five stars">{rating_value}
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">{review_count} reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">{download_count}</div>
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
            <div class="xg1aie">Last Updated: {last_updated}</div>
        </body>
    </html>
    '''
    result = get_app_info_from_html(mock_html)
    assert result == expected

#Test inputs as tuple[str, str, str, str, str]
@pytest.mark.parametrize("test_purpose, rating_value, review_count, download_count, last_updated, expected", COMPLETE_VALUE_TEST_BATTERY)
def test_get_gov_app_info_from_html(test_purpose: str, rating_value: str, review_count: str, download_count:str, last_updated: str, expected: tuple) -> None:
    # test when all the requested information is present
    mock_html = f'''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated {rating_value} stars out of five stars">{rating_value}
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">{review_count} reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div jslog="228772; 1:17686; track:impression;">
                                <span class="notranslate J3Ldd" aria-hidden="true">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 20 20" fill="none">
                                        <path d="M4.41669 14.9792L4.41669 7.91667L5.66669 7.91667L5.66669 14.9792L4.41669 14.9792ZM9.45835 14.9792L9.45835 7.91667L10.7084 7.91667L10.7084 14.9792L9.45835 14.9792ZM1.66669 17.4792L1.66669 16.2292L18.3334 16.2292L18.3334 17.4792L1.66669 17.4792ZM14.3334 14.9792L14.3334 7.91667L15.5834 7.91667L15.5834 14.9792L14.3334 14.9792ZM1.66669 6.66667L1.66669 5.5625L10 0.8125L18.3334 5.5625L18.3334 6.66667L1.66669 6.66667ZM4.45835 5.41667L15.5417 5.41667L10 2.25L4.45835 5.41667Z" fill="black"></path>
                                    </svg>
                                </span>
                            </div>
                        </div>
                        <div class="g1rdde">
                            <span aria-label="Government App">
                                <span>Government</span>
                            </span>
                            <div jscontroller="OuYqRc" jsaction="click:CnOdef" jslog="228772; 1:17801; track:click;" class="rXZODf" role="button" tabindex="0" aria-label="More info about the Government badge">
                                <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                            </div>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">{download_count}</div>
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
            <div class="xg1aie">Last Updated: {last_updated}</div>
        </body>
    </html>
    '''
    result = get_app_info_from_html(mock_html)
    assert result == expected

#Test inputs as tuple[str, str, str, str, str]
@pytest.mark.parametrize("test_purpose, rating_value, review_count, download_count, last_updated, expected", COMPLETE_VALUE_TEST_BATTERY)
def test_get_rewarded_app_info_from_html(test_purpose: str, rating_value: str, review_count: str, download_count:str, last_updated: str, expected: tuple) -> None:
    # test when all the requested information is present
    mock_html = f'''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated {rating_value} stars out of five stars">{rating_value}
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">{review_count} reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">{download_count}</div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <span class="notranslate YVLXxf" aria-hidden="true">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" xml:space="preserve">
                                    <rect fill="none" width="20" height="20"></rect>
                                    <path d="M10.54,11.09L8.66,9.22l-1.02,1.02l2.9,2.9l5.8-5.8l-1.02-1.01L10.54,11.09z M15.8,16.24H8.2L4.41,9.66L8.2,3h7.6l3.79,6.66 L15.8,16.24z M17,1H7L2,9.66l5,8.64V23l5-2l5,2v-4.69l5-8.64L17,1z"></path>
                                </svg>
                            </span>
                        </div>
                        <div class="g1rdde">Editors' Choice</div>
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
            <div class="xg1aie">Last Updated: {last_updated}</div>
        </body>
    </html>
    '''
    result = get_app_info_from_html(mock_html)
    assert result == expected

#Test inputs as tuple[str, str, str, str, str]
@pytest.mark.parametrize("test_purpose, rating_value, review_count, download_count, last_updated, expected", COMPLETE_VALUE_TEST_BATTERY)
def test_get_rewarded_gov_app_info_from_html(test_purpose: str, rating_value: str, review_count: str, download_count:str, last_updated: str, expected: tuple) -> None:
    # test when all the requested information is present
    mock_html = f'''
    <html>
        <body>
            <div class="l8YSdd">
                <div class="w7Iutd">
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div itemprop="starRating">
                                <div class="TT9eCd" aria-label="Rated {rating_value} stars out of five stars">{rating_value}
                                    <i class="google-material-icons notranslate ERwvGb" aria-hidden="true">star</i>
                                </div>
                            </div>
                        </div>
                        <div class="g1rdde">{review_count} reviews
                            
                            
                            <span class="z9nYqc" jscontroller="g1EWpd" jsaction="zDXV8" aria-label="Ratings and reviews are verified" role="button" tabindex="0">
                                <i class="google-material-icons notranslate yyf8A" aria-hidden="true">info</i>
                            </span>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <div jslog="228772; 1:17686; track:impression;">
                                <span class="notranslate J3Ldd" aria-hidden="true">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 20 20" fill="none">
                                        <path d="M4.41669 14.9792L4.41669 7.91667L5.66669 7.91667L5.66669 14.9792L4.41669 14.9792ZM9.45835 14.9792L9.45835 7.91667L10.7084 7.91667L10.7084 14.9792L9.45835 14.9792ZM1.66669 17.4792L1.66669 16.2292L18.3334 16.2292L18.3334 17.4792L1.66669 17.4792ZM14.3334 14.9792L14.3334 7.91667L15.5834 7.91667L15.5834 14.9792L14.3334 14.9792ZM1.66669 6.66667L1.66669 5.5625L10 0.8125L18.3334 5.5625L18.3334 6.66667L1.66669 6.66667ZM4.45835 5.41667L15.5417 5.41667L10 2.25L4.45835 5.41667Z" fill="black"></path>
                                    </svg>
                                </span>
                            </div>
                        </div>
                        <div class="g1rdde">
                            <span aria-label="Government App">
                                <span>Government</span>
                            </span>
                            <div jscontroller="OuYqRc" jsaction="click:CnOdef" jslog="228772; 1:17801; track:click;" class="rXZODf" role="button" tabindex="0" aria-label="More info about the Government badge">
                                <i class="google-material-icons notranslate oUaal" aria-hidden="true">info</i>
                            </div>
                        </div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">{download_count}</div>
                        <div class="g1rdde">Downloads</div>
                    </div>
                    <div class="wVqUob">
                        <div class="ClM7O">
                            <span class="notranslate YVLXxf" aria-hidden="true">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" xml:space="preserve">
                                    <rect fill="none" width="20" height="20"></rect>
                                    <path d="M10.54,11.09L8.66,9.22l-1.02,1.02l2.9,2.9l5.8-5.8l-1.02-1.01L10.54,11.09z M15.8,16.24H8.2L4.41,9.66L8.2,3h7.6l3.79,6.66 L15.8,16.24z M17,1H7L2,9.66l5,8.64V23l5-2l5,2v-4.69l5-8.64L17,1z"></path>
                                </svg>
                            </span>
                        </div>
                        <div class="g1rdde">Editors' Choice</div>
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
            <div class="xg1aie">Last Updated: {last_updated}</div>
        </body>
    </html>
    '''
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
    expected = ("Not Found", "1M+", "100K+",  "Jan 01, 2025")
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