var NGRes = new (function () {
    // Constants
    var NGRES_COMMENT_DIV_CLASSNAME = "ngid_comment";
    var POSTER_ID_SPAN_CLASSNAME = "res_poster_id";
    var NGID_TOGGLE_A_CLASSNAME = "ngid_toggle";
    var POSTER_NAME_SELECTOR = ".link_name1,.link_name2";
    var POSTER_NAME_CUT_SPAN_CLASSNAME = "cut_name";
    var NGRES_POSTER_NAME_SPAN_CLASSNAME = "ng_res";
    var NGRES_HIDE_ATTR_SPAN_CLASSNAME = "ng_hide";
    var POST_COUNT_SPAN_CLASSNAME_PREFIX = "hatugen_";
    var NGRES_COUNT_SPAN_CLASSNAME = "ngres_count";
    var NGNAME_TOGGLE_A_CLASSNAME = "ngname_toggle";

    // Cookie Constant
    var COOKIE_AVAILABLE_BYTE = 4093;
    var HISTORY_ID_COOKIE_NAME = "WEB_PATIO_HISTORY_ID";

    // Configurations from init.cgi (Initializing in initialize().)
    var NGRES_MESSAGE;
    var CHAIN_NG_COOKIE_KEY;
    var NGID_COOKIE_KEY;
    var NGID_COOKIE_LIMIT_REACHED_ERROR_MESSAGE;
    var NGNAME_COOKIE_KEY;
    var NGNAME_COOKIE_LIMIT_REACHED_ERROR_MESSAGE;
    var NGNAME_DISPLAY_CHARACTERS;
    var NGWORD_COOKIE_KEY;

    // Variables
    var ngResInfo = {
        ngid_array: void 0,
        ngname_array: {name: void 0, trip: void 0},
        ngword_array: void 0,
        chain_ng: void 0
    };
    var initialized = false;

    // Regex Constants
    var AND_SEPARATE_REGEX = /_/;
    var META_SPLIT_REGEX = /(\[[^\[\]]*\])/;
    var BRACKET_CAPTURE_REGEX = /^\[([^\[\]]*)\]$/;
    var IN_BRACKET_WORD_SEPARATE_REGEX = /\|/;
    var LINE_BREAK_SETTING_DETECT_REGEX = /^(?:\\n)+$/;
    var LINE_BREAKS_SEPARATE_REGEX = /((?:\\n)+)/g;
    var LINE_BREAK_COUNT_SPLIT_REGEX = /(\\n)/g;
    var LINE_BREAK_REGEX_STR = "\\n";

    // Compiled Regex Dictionary
    var compiled_regex_dic = {};

    // Settings Storage Communicator
    var SettingsStorageCommunicator = function (cookie_current_dirpath) {
        /**
         * Cookie Name Prefix
         *
         * @type {string}
         */
        var COOKIE_NAME_PREFIX = "WEB_PATIO_" + cookie_current_dirpath + "_";

        /**
         * Set Setting to Array
         *
         * @private
         * @param setKey Key to set array
         * @param setValue Set Value
         * @returns {boolean} Returns whether success to value set.
         */
        var setSetting_ = function (setKey, setValue) {
            switch (setKey) {
                case NGID_COOKIE_KEY:
                    ngResInfo.ngid_array = setValue;
                    break;
                case NGNAME_COOKIE_KEY:
                    ngResInfo.ngname_array = setValue;
                    break;
                case NGWORD_COOKIE_KEY:
                    ngResInfo.ngword_array = setValue;
                    break;
                case CHAIN_NG_COOKIE_KEY:
                    ngResInfo.chain_ng = setValue === 1;
                    break;
                default:
                    return false;
            }
            return true;
        };

        /**
         * All elements of array or object check whether empty.
         *
         * @private
         * @param array_or_object Check array or object
         * @returns {boolean} All of the elements of array or object is whether empty or not.
         */
        var inspectEmptyValue_ = function (array_or_object) {
            if ($.isArray(array_or_object)) {
                return array_or_object.length === 0;
            } else if ($.isPlainObject(array_or_object)) {
                var not_empty_count = 0;
                Object.keys(array_or_object).forEach(function (key) {
                    if (inspectEmptyValue_(array_or_object[key]) === false) {
                        not_empty_count++;
                    }
                });
                return not_empty_count === 0;
            } else {
                return false;
            }
        };

        /**
         * Settings Storage Communicator Interface
         *
         * @interface
         */
        var SettingsStorageCommunicatorInterface = function () {};
        /**
         * Load Settings from Storage.
         *
         * @param loadSequenceArray Specify the setting element to loading in the array,
         *                           elements are consists of an array of [load key or name, initial value, successful execution function, failed execution function].
         * @param finallyExecuteFunction Finally function always executed regardless of the loading results.
         */
        SettingsStorageCommunicatorInterface.prototype.loadSettings = function (loadSequenceArray, finallyExecuteFunction) {
            loadSequenceArray.forEach(function (element) {
                element[3](); // failed execution function
            });
            finallyExecuteFunction();
        };
        /**
         * Save Settings to Storage.
         *
         * @param saveValue Value to save.
         * @param saveNameOrKey Specify the key or name required to save.
         * @param successFunction Function to execute saving success.
         * @param failureFunction Function to execute saving failure.
         */
        SettingsStorageCommunicatorInterface.prototype.saveSettings = function (saveValue, saveNameOrKey, successFunction, failureFunction) { failureFunction(); };

        /**
         * HistoryLog Storage Communicator Class
         *
         * @type {Object}
         * @implements {SettingsStorageCommunicatorInterface}
         */
        var HistoryLogCommunicator = function () {
            this.api_url = './ngsettings_api.cgi';
        };
        $.extend(HistoryLogCommunicator.prototype, SettingsStorageCommunicatorInterface.prototype, {
            /**
             * Load Settings from HistoryLog.
             *
             * @override
             * @param loadSequenceArray Specify the setting element to loading in the array,
             *                           elements are consists of an array of [load key or name, initial value, successful execution function, failed execution function].
             * @param finallyExecuteFunction Finally function always executed regardless of the loading results.
             */
            loadSettings: function (loadSequenceArray, finallyExecuteFunction) {
                $.ajax({
                    url: this.api_url,
                    method: 'GET',
                    dataType: 'json',
                    async: true,
                    cache: false,
                    timeout: 5000,
                    success: function (json_parsed_array) {
                        loadSequenceArray.forEach(function (element) {
                            if (element[0] in json_parsed_array) {
                                var setValue = json_parsed_array[element[0]];
                                if (element[0] === CHAIN_NG_COOKIE_KEY) {
                                    setValue = Number(setValue);
                                }
                                if (setSetting_(element[0], setValue)) {
                                    element[2](); // value set successfully
                                } else {
                                    element[3](); // value set failed
                                }
                            } else {
                                // key is not found in loading settings
                                if (setSetting_(element[0], element[1])) {
                                    element[2](); // initial value set successfully
                                } else {
                                    element[3](); // initial value set failed
                                }
                            }
                        });
                        finallyExecuteFunction();
                    },
                    error: function () {
                        loadSequenceArray.forEach(function (element) {
                            element[3](); // loading failed
                        });
                        finallyExecuteFunction();
                    }
                });
            },
            /**
             * Asynchronously Save Settings to HistoryLog
             *
             * @override
             * @param saveValue Value to save.
             * @param saveKey Key required to save to HistoryLog.
             * @param successFunction Function to execute loading success.
             * @param failureFunction Function to execute loading failure.
             */
            saveSettings: function (saveValue, saveKey, successFunction, failureFunction) {
                var jsonEncodedValue = JSON.stringify(saveValue);
                var sendData = {};
                sendData[saveKey] = jsonEncodedValue;
                $.ajax({
                    url: this.api_url,
                    method: 'POST',
                    async: true,
                    cache: false,
                    timeout: 5000,
                    data: sendData,
                    success: successFunction,
                    error: failureFunction
                });
            }
        });

        /**
         * Cookie Storage Communicator Class
         *
         * @type {Object}
         * @implements {SettingsStorageCommunicatorInterface}
         */
        var CookieCommunicator = function () {};
        $.extend(CookieCommunicator.prototype, SettingsStorageCommunicatorInterface.prototype, {
            /**
             * Load Settings from Cookie
             *
             * @override
             * @param loadSequenceArray Specify the setting element to loading in the array,
             *                           elements are consists of an array of [load key or name, initial value, successful execution function, failed execution function].
             * @param finallyExecuteFunction Finally function always executed regardless of the loading results.
             */
            loadSettings: function (loadSequenceArray, finallyExecuteFunction) {
                var cookie_name_suffix_capture_regexp = new RegExp("^" + COOKIE_NAME_PREFIX + "(.*)");
                var cookies = {};
                document.cookie.split(/; */).forEach(function (key_value_str) {
                    var key_value_pair = key_value_str.split("=");
                    var match_result = cookie_name_suffix_capture_regexp.exec(key_value_pair[0]);
                    if (match_result !== null) {
                        cookies[match_result[1]] = decodeURIComponent(key_value_pair[1]);
                    }
                });

                loadSequenceArray.forEach(function (element) {
                    if (element[0] in cookies) {
                        var setValue = cookies[element[0]];
                        if (element[0] === CHAIN_NG_COOKIE_KEY) {
                            setValue = Number(setValue);
                        } else {
                            setValue = JSON.parse(setValue);
                        }
                        if (setSetting_(element[0], setValue)) {
                            element[2](); // value set successfully
                        } else {
                            element[3](); // value set failed
                        }
                    } else {
                        // key is not found in loading settings
                        if (setSetting_(element[0], element[1])) {
                            element[2](); // initial value set successfully
                        } else {
                            element[3](); // initial value set failed
                        }
                    }
                });
                finallyExecuteFunction();
            },
            /**
             * Save Settings To Cookie
             *
             * @override
             * @param saveValue Value to save.
             * @param saveName CookieName required to save.
             * @param successFunction Function to execute loading success.
             * @param failureFunction Function to execute loading failure.
             * @param cookieLimitExceedMessage Error message when exceed the Cookie storage limit.
             */
            saveSettings: function (saveValue, saveName, successFunction, failureFunction, cookieLimitExceedMessage) {
                var cookieName = COOKIE_NAME_PREFIX + saveName;
                if (inspectEmptyValue_(saveValue)) {
                    document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
                } else {
                    var jsonEncodedValue = encodeURIComponent(JSON.stringify(saveValue));
                    if ((cookieName.length + jsonEncodedValue.length) > COOKIE_AVAILABLE_BYTE) {
                        alert(cookieLimitExceedMessage);
                        failureFunction();
                    }
                    document.cookie = cookieName + "=" + jsonEncodedValue + "; expires=Tue, 19 Jan 2038 03:14:06 GMT";
                }
                successFunction();
            }
        });

        /**
         * HistoryLogCommunicator Instance
         *
         * @type {HistoryLogCommunicator}
         */
        var history_log_communicator = new HistoryLogCommunicator();

        /**
         * CookieCommunicator Instance
         *
         * @type {CookieCommunicator}
         */
        var cookie_communicator = new CookieCommunicator();

        /**
         * Returns whether or not already logged in HistoryID
         *
         * @returns {boolean} Whether or not already logged in HistoryID
         */
        var isHistoryIDLoggedIn = function () {
            var cookies = document.cookie.split(/; */);
            for (var i = 0; i < cookies.length; i++) {
                var cookiePair = cookies[i].split("=");
                if (cookiePair[0] === HISTORY_ID_COOKIE_NAME) {
                    return true;
                }
            }
            return false;
        };

        /**
         * Returns instance of appropriate class depending on the situation
         *
         * @returns {SettingsStorageCommunicatorInterface} Instance of Storage Communicator
         */
        var currentStorageCommunicator = function () {
            if (isHistoryIDLoggedIn()) {
                return history_log_communicator;
            } else {
                return cookie_communicator;
            }
        };

        /**
         * Load NG Settings from Storage
         *
         * @param loadSequenceArray Specify the setting element to loading in the array,
         *                           elements are consists of an array of [load key or name, initial value, successful execution function, failed execution function].
         * @param finallyExecuteFunction Finally function always executed regardless of the loading results.
         */
        this.loadSettings = function (loadSequenceArray, finallyExecuteFunction) {
            currentStorageCommunicator().loadSettings(loadSequenceArray, finallyExecuteFunction);
        };

        /**
         * Save NG Settings to Storage
         *
         * @param saveValue Value to save.
         * @param saveNameOrKey Key or Name required to save.
         * @param successFunction Function to execute saving success.
         * @param failureFunction Function to execute saving failure.
         * @param cookieLimitExceedMessage Error message when exceed the Cookie storage limit.
         */
        this.saveSettings = function (saveValue, saveNameOrKey, successFunction, failureFunction, cookieLimitExceedMessage) {
            currentStorageCommunicator().saveSettings(saveValue, saveNameOrKey, successFunction, failureFunction, cookieLimitExceedMessage);
        }
    };

    // Settings Storage Communicator Instance (Initialize in initialize())
    /**
     * Settings Storage Communicator Instance
     *
     * @type {SettingsStorageCommunicator}
     */
    var settings_storage_communicator;

    /**
     * Check whether NGID response
     * @param resElement
     * @returns {boolean}
     */
    var isNGID = function (resElement) {
        if (NGID_COOKIE_KEY !== void 0) {
            var id = $(resElement).find("span." + POSTER_ID_SPAN_CLASSNAME).first().text();
            return $.inArray(id, ngResInfo.ngid_array) !== -1;
        }
    };

    /**
     * Check whether NGName response
     * @param resElement
     * @returns {boolean}
     */
    var isNGName = function (resElement) {
        if (NGNAME_COOKIE_KEY !== void 0) {
            // try to split name and trip
            var tripsplit_array = splitName($(resElement).find(POSTER_NAME_SELECTOR).filter('span').first().text().replace(/ \[sage] /, ''));
            var flg = tripsplit_array[0] !== null ? partialMatchInArray(tripsplit_array[0], ngResInfo.ngname_array.name) !== null : false;
            if (flg === false && tripsplit_array[1] !== null) {
                flg = $.inArray(tripsplit_array[1], ngResInfo.ngname_array.trip) !== -1;
            }
            return flg;
        }
    };

    /**
     * Check whether NGWord response
     * @param resElement
     * @returns {boolean}
     */
    var isNGWord = function (resElement) {
        var resContent = $(resElement).children(".comment").html()
                            .replace(/<br>/ig, "\n")
                            .replace(/&amp;/g, "&")
                            .replace(/&lt;/g, "<")
                            .replace(/&gt;/g, ">")
                            .replace(/&quot;/g, "\"")
                            .replace(/&#039;/g, "'")
                            .replace(/<("[^"]*"|'[^']*'|[^'">])*>/g, "");
        var matchArray = partialMatchInArray(resContent, ngResInfo.ngword_array, true, true);
        return matchArray !== null;
    };

    /**
     * Check whether it's possible to show comment
     * @param resElement
     * @returns {boolean}
     */
    var canShowCommentAbbr = function (resElement) {
        var ngflg = false;
        if (NGID_COOKIE_KEY !== void 0) {
            // check whether is NGID
            ngflg = isNGID(resElement);
        }
        if (NGNAME_COOKIE_KEY !== void 0) {
            // check whether is NGName
            ngflg = ngflg || isNGName(resElement);
        }
        return !ngflg && (isNGWord(resElement) || NGRes.isChainNGRes(resElement));
    };

    /**
     * Return elements that string partial matches in array
     * @param {string} targetString
     * @param {Array.<string>} checkArray
     * @param {boolean=} isRegexMatching
     * @param {boolean=} isLineBreakIncludeJudge
     * @returns {?Array.<number>}
     */
    var partialMatchInArray = function (targetString, checkArray, isRegexMatching, isLineBreakIncludeJudge) {
        if (checkArray === void 0) {
            return null;
        }
        var matchIndexArray = [];
        for (var i = 0; i < checkArray.length; i++) {
            if (checkArray[i] === '') {
                continue;
            }
            if (isRegexMatching &&
                ((isLineBreakIncludeJudge && LINE_BREAK_SETTING_DETECT_REGEX.test(checkArray[i]))
                    || AND_SEPARATE_REGEX.test(checkArray[i]) || BRACKET_CAPTURE_REGEX.test(checkArray[i]))) {
                if (regexMatch(targetString, checkArray[i], isLineBreakIncludeJudge)) {
                    matchIndexArray.push(i);
                }
            } else {
                if (targetString.indexOf(checkArray[i]) !== -1) {
                    matchIndexArray.push(i);
                }
            }
        }
        return matchIndexArray.length > 0 ? matchIndexArray : null;
    };

    /**
     * Split name and trip by trip separator
     * @param namebox_text
     * @returns {*[]}
     */
    var splitName = function (namebox_text) {
        if (NGNAME_COOKIE_KEY !== void 0) {
            var tripsplit_array = namebox_text.split("◆");
            var name = tripsplit_array.length === 1 || tripsplit_array[0].length > 0 ? tripsplit_array[0] : null;
            var trip = tripsplit_array.length === 2 ? tripsplit_array[1] : null;
            return [name, trip];
        }
    };

    /**
     * Escape regex character in string
     * @param {string} string
     * @returns {string}
     */
    var escapeRegExp = function (string) {
        // ref: https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Regular_Expressions#Using_Special_Characters
        return (string + "").replace(/([.*+?^=!:${}()|[\]\/\\])/g, "\\$1");
    };

    /**
     * Escape regex character exclude linebreak in string
     * @param {string} string
     * @returns {string}
     */
    var lineBreakExcludeRegexEscaping = function (string) {
        var regex_str = "";
        var lineBreakSplitArray = string.split(LINE_BREAKS_SEPARATE_REGEX);
        for (var i = 0; i < lineBreakSplitArray.length; i++) {
            if (i % 2 === 0) {
                regex_str += escapeRegExp(lineBreakSplitArray[i]);
            } else {
                var capture_array = lineBreakSplitArray[i].match(LINE_BREAK_COUNT_SPLIT_REGEX);
                if (capture_array.length > 1) {
                    regex_str += "^" + LINE_BREAK_REGEX_STR + "{" + capture_array.length + "," + "}"
                } else {
                    regex_str += "^" + LINE_BREAK_REGEX_STR + "+";
                }
            }
        }
        return regex_str;
    };

    /**
     *  Return whether targetString match to checkString
     * @param {string} targetString
     * @param {string} checkString
     * @param {boolean=} isLineBreakIncludeJudge
     * @returns {boolean}
     */
    var regexMatch = function (targetString, checkString, isLineBreakIncludeJudge) {
        var i;
        if (checkString in compiled_regex_dic === false) {
            // split by "_"(AND) separator
            var exp_count = {};
            var and_set = jQuery.grep(checkString.split(AND_SEPARATE_REGEX), function (val) {
                if (val === "") {
                    return false;
                }
                // duplicate(repeat) count
                if (val in exp_count) {
                    exp_count[val]++;
                    return false;
                } else {
                    exp_count[val] = 1;
                    return true;
                }
            });
            if (and_set.length === 0) {
                return false;
            }

            var and_regex_array = [];
            for (i = 0; i < and_set.length; i++) {
                var isMultiLineJudge = false;
                var regex_str = "";
                var meta_splitted_set = jQuery.grep(and_set[i].split(META_SPLIT_REGEX), function (val) {
                    return val !== "";
                });
                for (var j = 0; j < meta_splitted_set.length; j++) {
                    var in_bracket_word_array = BRACKET_CAPTURE_REGEX.exec(meta_splitted_set[j]);
                    if (in_bracket_word_array !== null) {
                        var in_bracket_word_separated_array = jQuery.grep(in_bracket_word_array[1].split(IN_BRACKET_WORD_SEPARATE_REGEX), function (val) {
                            return val !== "";
                        });
                        if (in_bracket_word_separated_array.length === 1) {
                            regex_str += "[" + escapeRegExp(in_bracket_word_separated_array[0]) + "]";
                        } else if (in_bracket_word_separated_array.length > 1) {
                            var word_array = [];
                            for (var k = 0; k < in_bracket_word_separated_array.length; k++) {
                                word_array.push(escapeRegExp(in_bracket_word_separated_array[k]));
                            }
                            regex_str += "(?:" + word_array.join("|") + ")";
                        }
                    } else {
                        if (isLineBreakIncludeJudge && LINE_BREAK_SETTING_DETECT_REGEX.test(meta_splitted_set[j])) {
                            regex_str += lineBreakExcludeRegexEscaping(meta_splitted_set[j]);
                            isMultiLineJudge = true;
                        } else {
                            regex_str += escapeRegExp(meta_splitted_set[j]);
                        }
                    }
                }
                if (regex_str !== "") {
                    var regex_options = isMultiLineJudge ? "mg" : "g";
                    and_regex_array.push([new RegExp(regex_str, regex_options), exp_count[and_set[i]]]);
                }
            }
            if (and_regex_array.length > 0) {
                compiled_regex_dic[checkString] = and_regex_array;
            } else {
                compiled_regex_dic[checkString] = null;
            }
        }
        // match judge by regex in dic
        if (compiled_regex_dic[checkString] === null) {
            return false;
        }
        for (i = 0; i < compiled_regex_dic[checkString].length; i++) {
            var matchResult = targetString.match(compiled_regex_dic[checkString][i][0]);
            if (matchResult === null || matchResult.length < compiled_regex_dic[checkString][i][1]) {
                return false;
            }
        }
        return true;
    };

    /**
     * Define onclick event NGID/NGName toggle element
     */
    var addNGIDandNGNameClickEvent = function () {
        var ngid_target = NGID_COOKIE_KEY !== void 0 ? $("a." + NGID_TOGGLE_A_CLASSNAME).css("display", "inline") : null;
        var ngname_target = NGNAME_COOKIE_KEY !== void 0 ? $("a." + NGNAME_TOGGLE_A_CLASSNAME).css("display", "inline") : null;
        if (ngid_target !== null) {
            ngid_target.click(function () {
                ngid_target.off("click");
                ngname_target.off("click");
                NGRes.toggleNGIDRegistState($(this));
                return false;
            });
        }
        if (ngname_target !== null) {
            ngname_target.click(function () {
                ngname_target.off("click");
                ngid_target.off("click");
                NGRes.toggleNGNameRegistState($(this));
                return false;
            });
        }
    };

    /**
     * Check whether Chained NG response
     * @param resElement
     * @returns {boolean}
     */
    this.isChainNGRes = function (resElement) {
        if (ngResInfo.chain_ng) {
            var currentRes = $(resElement);
            if (currentRes.length === 1) {
                var currentResNumber = currentRes.attr("id").replace(/^d/, "");
                var anchor_array = currentRes.children(".comment").children(".scroll").text().match(/>{2}\d{1,3}/g);
                if (anchor_array !== null) {
                    for (var i = 0; i < anchor_array.length; i++) {
                        var resNumber = anchor_array[i].replace(/^>{2}/, "");
                        if (resNumber === currentResNumber) {
                            continue;
                        }
                        var anchorDestElement = $("div[id=d" + resNumber + "]");
                        if (anchorDestElement.length > 0 && (NGRes.isNGRes(anchorDestElement) || NGRes.isChainNGRes(anchorDestElement))) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    };

    /**
     * Check whether NG(NGID/NGName/NGWord) response
     * @param resElement
     * @returns {boolean}
     */
    this.isNGRes = function (resElement) {
        var flg = false;
        if (NGID_COOKIE_KEY !== void 0) {
            // check whether is NGID
            flg = isNGID(resElement);
        }
        if (NGNAME_COOKIE_KEY !== void 0) {
            // check whether is NGName
            flg = flg || isNGName(resElement);
        }
        // check whether is NGWord
        flg = flg || isNGWord(resElement);
        return flg;
    };

    /**
     * Set all comment display state(NG/ChainedNG/Reference)
     */
    this.setAllCommentStatus = function () {
        $("div[id^=d]").each(function () {
            // show or hide comment, date, id
            var all_name = $(this).find(POSTER_NAME_SELECTOR).filter('span').first();
            var ngHideSpan = $(this).find("span." + NGRES_HIDE_ATTR_SPAN_CLASSNAME).first();
            var countSpan = $(this).find("span[class^=" + POST_COUNT_SPAN_CLASSNAME_PREFIX + "]");
            var commentDiv = $(this).children("div.comment").first();
            var commentImgDiv = commentDiv.next("div.comment-img");
            var ngResCommentDiv = commentDiv.prev("div." + NGRES_COMMENT_DIV_CLASSNAME);
            var commentAbbr = $(this).find("abbr").first();

            if (NGRes.isNGRes($(this)) || NGRes.isChainNGRes($(this))) {
                all_name.addClass(NGRES_POSTER_NAME_SPAN_CLASSNAME);
                ngHideSpan.hide();
                countSpan.addClass(NGRES_COUNT_SPAN_CLASSNAME);
                if (ngResCommentDiv.length === 0) {
                    ngResCommentDiv = $('<div class="' + NGRES_COMMENT_DIV_CLASSNAME + '">' + NGRES_MESSAGE + '</div>');
                    commentDiv.before(ngResCommentDiv);
                }
                ngResCommentDiv.show();
                if (canShowCommentAbbr($(this))) {
                    if (commentAbbr.length === 0) {
                        var resInfoLastElement = all_name.nextAll('br').first().prev();
                        if (resInfoLastElement.length === 0) {
                            resInfoLastElement = all_name.nextAll().last();
                        }
                        var resComment = commentDiv.text();
                        commentAbbr = $('<abbr rel="tooltip" style="text-decoration:underline">元レス</abbr>')
                            .attr("title", resComment);
                        resInfoLastElement.after(commentAbbr);
                        commentAbbr.before(" ")
                    }
                    commentAbbr.show();
                } else if (commentAbbr.length === 1) {
                    commentAbbr.hide();
                }
                commentDiv.hide();
                if (commentImgDiv.length === 1) {
                    commentImgDiv.hide();
                }
            } else if (commentDiv.css("display") === "none") {
                all_name.removeClass(NGRES_POSTER_NAME_SPAN_CLASSNAME);
                ngHideSpan.show();
                countSpan.removeClass(NGRES_COUNT_SPAN_CLASSNAME);
                ngResCommentDiv.hide();
                if (commentAbbr.length === 1) {
                    commentAbbr.hide();
                }
                commentDiv.show();
                if (commentImgDiv.length === 1) {
                    commentImgDiv.show();
                }
            }

            // NGID
            if (NGID_COOKIE_KEY !== void 0) {
                var ngid_toggle_element = all_name.nextAll("a." + NGID_TOGGLE_A_CLASSNAME).first();
                if (isNGID($(this))) {
                    ngid_toggle_element.text("IDを戻す").addClass("enabled");
                } else {
                    ngid_toggle_element.text("ID").removeClass("enabled");
                }
            }

            // NGName
            if (NGNAME_COOKIE_KEY !== void 0) {
                var ngname_toggle_element = all_name.nextAll("a." + NGNAME_TOGGLE_A_CLASSNAME).first();
                var ngname_cut_element = all_name.children("span." + POSTER_NAME_CUT_SPAN_CLASSNAME).first();
                if (isNGName($(this))) {
                    ngname_toggle_element.text("名前を戻す").addClass("enabled");
                    if (ngname_cut_element.length === 1) {
                        ngname_cut_element.hide();
                    }
                } else {
                    ngname_toggle_element.text("名前").removeClass("enabled");
                    if (ngname_cut_element.length === 1) {
                        ngname_cut_element.show();
                    }
                }
            }

            // ChainNG
            var chain_name = all_name.nextAll("span.chain_name").first();
            if (NGRes.isNGRes($(this)) === false && NGRes.isChainNGRes($(this))) {
                if (chain_name.length === 0) {
                    chain_name = $('<span class="chain_name">連鎖</span>');
                    all_name.after(chain_name);
                }
                all_name.hide();
                chain_name.show();
            } else {
                if (chain_name.length === 1) {
                    chain_name.hide();
                }
                all_name.show();
            }
        });

        // cooperate with referenced response related function
        RefRes.updateCounterAndIndentedBlockDisplayState();
    };

    /**
     * Toggle poster ID regist state in NGID list.
     * @param ngid_toggle_element
     */
    this.toggleNGIDRegistState = function (ngid_toggle_element) {
        if (NGID_COOKIE_KEY !== void 0) {
            var ngid = $(ngid_toggle_element).prevAll("span." + NGRES_HIDE_ATTR_SPAN_CLASSNAME).first().children("span." + POSTER_ID_SPAN_CLASSNAME).first().text();
            // get ngid index in array
            var existIndex = $.inArray(ngid, ngResInfo.ngid_array);
            // regist/unregist NGID
            if (existIndex === -1) { // regist NGID
                ngResInfo.ngid_array.push(ngid);
            } else { // unregist NGID
                ngResInfo.ngid_array.splice(existIndex, 1);
            }

            // update comment display status
            NGRes.setAllCommentStatus();

            // save cookie or history log
            settings_storage_communicator.saveSettings(
                ngResInfo.ngid_array,
                NGID_COOKIE_KEY,
                addNGIDandNGNameClickEvent, // on success
                function () { // on failure
                    // try to (un)registering NGID, but regist error occurred.
                    if (existIndex === -1) {
                        // re-unregist
                        ngResInfo.ngid_array.pop();
                    } else {
                        // re-regist
                        ngResInfo.ngid_array.splice(existIndex, 0, ngid);
                    }
                    NGRes.setAllCommentStatus(); // revert comment display status
                    addNGIDandNGNameClickEvent();
                },
                NGID_COOKIE_LIMIT_REACHED_ERROR_MESSAGE
            );
        }
    };

    /**
     * Toggle poster name regist state in NGName list.
     * @param ngname_toggle_element
     */
    this.toggleNGNameRegistState = function (ngname_toggle_element) {
        // get name/trip index in array
        var tripsplit_array = splitName($(ngname_toggle_element).prevAll(POSTER_NAME_SELECTOR).filter('span').first().text().replace(/ \[sage] /, ''));
        var nameExistIndexArray = tripsplit_array[0] !== null ? partialMatchInArray(tripsplit_array[0], ngResInfo.ngname_array.name) : null;
        var tripExistIndex = tripsplit_array[1] !== null ? $.inArray(tripsplit_array[1], ngResInfo.ngname_array.trip) : -1;

        // treat array copy
        var treat_name = null;
        var treat_trip = null;

        // regist/unregist NGName
        if (nameExistIndexArray !== null || tripExistIndex > -1) { // unregist NGName
            if (nameExistIndexArray !== null) { // unregist name
                treat_name = [];
                for (var i = nameExistIndexArray.length - 1; 0 <= i; i--) {
                    var splice_name = ngResInfo.ngname_array.name.splice(nameExistIndexArray[i], 1)[0];
                    treat_name.unshift([nameExistIndexArray[i], splice_name]);
                }
            }
            if (tripExistIndex > -1) { // unregist trip
                ngResInfo.ngname_array.trip.splice(tripExistIndex, 1);
                treat_trip = [tripExistIndex, tripsplit_array[1]];
            }
        } else { // regist NGName
            if (nameExistIndexArray === null && tripsplit_array[0] !== null) { // regist name
                ngResInfo.ngname_array.name.push(tripsplit_array[0]);
                treat_name = -1;
            }
            if (tripExistIndex === -1 && tripsplit_array[1] !== null) { // regist trip
                ngResInfo.ngname_array.trip.push(tripsplit_array[1]);
                treat_trip = -1;
            }
        }

        // update comment display status
        NGRes.setAllCommentStatus();

        // save cookie or history log
        settings_storage_communicator.saveSettings(
            ngResInfo.ngname_array,
            NGNAME_COOKIE_KEY,
            addNGIDandNGNameClickEvent, // on success
            function () { // on failure
                // try to (un)registering NGName, but regist error occurred.
                if (treat_name !== null) {
                    if ($.isArray(treat_name)) {
                        treat_name.forEach(function (index_name_pair) {
                            // re-regist name
                            ngResInfo.ngname_array.name.splice(index_name_pair[0], 0, index_name_pair[1]);
                        });
                    } else {
                        // re-unregist name
                        ngResInfo.ngname_array.name.pop();
                    }
                }
                if (treat_trip !== null) {
                    if ($.isArray(treat_trip)) {
                        ngResInfo.ngname_array.trip.splice(treat_trip[0], 0, treat_trip[1]);
                    } else {
                        // re-unregist trip
                        ngResInfo.ngname_array.trip.pop();
                    }
                }
                NGRes.setAllCommentStatus(); // revert comment display status
                addNGIDandNGNameClickEvent();
            },
            NGNAME_COOKIE_LIMIT_REACHED_ERROR_MESSAGE
        );
    };

    /**
     * onLoad event
     */
    // バグがあるのでコメントアウト、cが定義されていない
    $(function () {
        var initialize = function () {
            var config = c('TkdJRA=='); // 'TkdJRA==' == 'NGID'(Base64Encode)

            // Initialize
            if (initialized === false) {
                // Initialize Settings Storage Communicator
                settings_storage_communicator = new SettingsStorageCommunicator(config.cookie_current_dirpath);

                // set variable
                NGRES_MESSAGE = config.ngres_message;
                if (config.use_ngid) {
                    NGID_COOKIE_LIMIT_REACHED_ERROR_MESSAGE = config.ngid_cookie_limit_reached_error_message;
                    NGID_COOKIE_KEY = "NGID_LIST";
                }
                if (config.use_ngname) {
                    NGNAME_COOKIE_LIMIT_REACHED_ERROR_MESSAGE = config.ngname_cookie_limit_reached_error_message;
                    NGNAME_DISPLAY_CHARACTERS = config.ngname_display_characters;
                    NGNAME_COOKIE_KEY = "NGNAME_LIST";
                }
                NGWORD_COOKIE_KEY = "NGWORD_LIST";
                CHAIN_NG_COOKIE_KEY = "CHAIN_NG";

                initialized = true;
            } else {
                // Remove NGID / NGName Click Event
                if (NGID_COOKIE_KEY !== void 0) {
                    $("a." + NGID_TOGGLE_A_CLASSNAME).css("display", "inline").off("click");
                }
                if (NGNAME_COOKIE_KEY !== void 0) {
                    $("a." + NGNAME_TOGGLE_A_CLASSNAME).css("display", "inline").off("click");
                }
            }

            // Prepare NG Settings Load Sequence Array
            var ng_settings_load_sequence_array = [];

            if (config.use_ngid) {
                // read cookie or history log
                ng_settings_load_sequence_array.push([
                    NGID_COOKIE_KEY,
                    [],
                    function () {}, // on success
                    function () {} // on failure
                ]);
            }

            if (config.use_ngname) {
                // read cookie or history log
                ng_settings_load_sequence_array.push([
                    NGNAME_COOKIE_KEY,
                    { name:[], trip:[] },
                    function () {}, // on success
                    function () {} // on failure
                ]);
            }

            // read ngword cookie or history log and set to textarea
            ng_settings_load_sequence_array.push([
                NGWORD_COOKIE_KEY,
                [],
                function () { // on success
                    $("#ngwords_textarea").val(ngResInfo.ngword_array.join("\n"));
                },
                function () {} // on failure
            ]);

            // read chain ng state cookie or history log and set status
            ng_settings_load_sequence_array.push([
                CHAIN_NG_COOKIE_KEY,
                config.chain_ng,
                function () { // on success
                    $("#chain_ng_status").text(ngResInfo.chain_ng ? "有効" : "無効");

                    var chain_ng_form = $("#chain_ng_form");
                    if (chain_ng_form.length > 0) {
                        chain_ng_form[0].reset();
                    }
                },
                function () {} // on failure
            ]);

            // Perform load settings
            settings_storage_communicator.loadSettings(ng_settings_load_sequence_array, function () {
                NGRes.setAllCommentStatus();
                RefRes.updateCounterAndIndentedBlockDisplayState();
                addNGIDandNGNameClickEvent();
            });
        };

        initialize();

        // this event triggered by history.back() on firefox / safari
        // other browser trigger onLoad event
        $(window).on("pageshow", null, {initialize: initialize}, function (event) {
            if (event.originalEvent.persisted) {
                event.data.initialize();
            }
        });
    });
})();

// define referenced response counting and indented displaying function
var RefRes = new (function () {
    // Constants
    var REFERENCE_RESPONSE_INDENTED_BLOCK_DIV_CLASSNAME = "refRes";

    // Configurations from init.cgi (Initializing in initialize().)
    var NGRES_HIDE_REFERENCE_COUNTER;
    var NUMBER_OF_ANCHOR_MADE_REF_COUNT_EXEMPT;

    // Variables
    var refInfoPerRes = {};

    /**
     * Update reference response counter and indented block display State
     */
    this.updateCounterAndIndentedBlockDisplayState = function () {
        // update indented block display state
        // find response element under reference response indented block
        $("div." + REFERENCE_RESPONSE_INDENTED_BLOCK_DIV_CLASSNAME).children("div[id^=d]").each(function () {
            // check whether is not ChainNG response
            if (NGRes.isChainNGRes($(this)) === false && NGRes.isNGRes($(this)) === false) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });

        // update reference response counter value
        for (var resNo in refInfoPerRes) {
            if (refInfoPerRes[resNo] === null) {
                continue;
            }

            // common usage variables
            var i, counter;

            // hide counter if root response is ChainNG/NG
            var resParent = refInfoPerRes[resNo][0][0].parent().parent().parent();
            var hideCounterByNGRes = NGRES_HIDE_REFERENCE_COUNTER && (NGRes.isChainNGRes(resParent) || NGRes.isNGRes(resParent));
            if (hideCounterByNGRes) {
                for (i = 0; i < refInfoPerRes[resNo][0].length; i++) {
                    counter = refInfoPerRes[resNo][0][i];
                    counter.text("").hide();
                }
                // skip visible reference counting
                continue;
            }

            // count visible reference response
            var reference_count = 0;
            for (var refResNo in refInfoPerRes[resNo][1]) {
                if (refInfoPerRes[resNo][1].hasOwnProperty(refResNo) === false) {
                    continue;
                }
                var refResElement = refInfoPerRes[resNo][1][refResNo];
                if (refResElement.children("div.comment").first().css("display") === "block") {
                    // count only comment displayed response (it's not NG response)
                    reference_count++;
                }
            }

            // update counter value
            for (i = 0; i < refInfoPerRes[resNo][0].length; i++) {
                counter = refInfoPerRes[resNo][0][i];
                if (reference_count === 0) {
                    counter.text("").hide();
                } else {
                    counter.text(reference_count + "件のレス").show();
                }
            }
        }
    };

    /**
     * onLoad event
     */
    // バグがあるのでコメントアウト、cが定義されていない
    $(function () {
        var config = c('UmVmUmVz'); // 'UmVmUmVz' == 'RefRes'(Base64Encode)
        NGRES_HIDE_REFERENCE_COUNTER = config.ngres_hide_reference_counter;
        NUMBER_OF_ANCHOR_MADE_REF_COUNT_EXEMPT = config.number_of_anchor_made_ref_count_exempt;

        // count reference
        $("div.main").children("div[id^=d]").each(function () {
            var resParent = $(this);
            var resNo = parseInt(resParent.attr("id").replace(/^d/, ""), 10);
            // count per anchor
            var refReses = resParent.children("div.comment").first().children("a.scroll");
            if (refReses.length < NUMBER_OF_ANCHOR_MADE_REF_COUNT_EXEMPT) {
                refReses.each(function () {
                    var element = $(this);
                    var refResNo = parseInt(element.attr("href").replace(/^#/, ""), 10);
                    if (refResNo >= resNo) {
                        // ignore self or future reference response number
                        return true;
                    }
                    if (refResNo in refInfoPerRes) {
                        if (refInfoPerRes[refResNo] !== null) {
                            // add reponse parent element to PosterID/ParentElement array
                            refInfoPerRes[refResNo][1][resNo] = resParent;
                        }
                    } else {
                        var refResParent = $("#d" + refResNo);
                        if (refResParent.length === 1) {
                            // create counter element
                            var counter = $("<span class='hi_sanshou'></span>").insertAfter(
                                $("<br>").insertAfter(
                                    refResParent.find("dt").first().children().last()
                                )
                            );
                            // set reference response indented display function event
                            counter.click(function () {
                                var resParent = $(this).parents("#d" + refResNo).first();
                                if (resParent.children("div.comment").first().css("display") !== "block") {
                                    // ignore counter click in NG response
                                    return;
                                }
                                var refResBlock = resParent.children("div." + REFERENCE_RESPONSE_INDENTED_BLOCK_DIV_CLASSNAME).first();
                                if (refResBlock.length === 0) {
                                    // create reference response indented block element
                                    refResBlock = $("<div class='" + REFERENCE_RESPONSE_INDENTED_BLOCK_DIV_CLASSNAME + "'></div>");
                                    // append reference response element to indented block
                                    for (var resNo in refInfoPerRes[refResNo][1]) {
                                        if (refInfoPerRes[refResNo][1].hasOwnProperty(resNo) === false) {
                                            continue;
                                        }
                                        var element = refInfoPerRes[refResNo][1][resNo];
                                        var cloneElement = element.clone(true, true);
                                        // remove indented reference response
                                        cloneElement.children("div.comment").first().children("div." + REFERENCE_RESPONSE_INDENTED_BLOCK_DIV_CLASSNAME).first().remove();
                                        // capture clone reference counter
                                        var counter = cloneElement.find("dt").first().children("span.hi_sanshou").first();
                                        if (counter.length === 1) {
                                            refInfoPerRes[resNo][0].push(counter);
                                        }
                                        if (NGRes.isChainNGRes(element) || NGRes.isNGRes(element)) {
                                            cloneElement.hide();
                                        }
                                        // append to indented block
                                        refResBlock.append(cloneElement);
                                    }
                                    // append indented block to comment block
                                    resParent.append(refResBlock);
                                } else {
                                    // toggle indented block display status
                                    refResBlock.toggle();
                                }
                            });
                            // create response reference information array
                            // refInfoPerRes[refResNo][0] : reference counter elements array (include same resNo indented displayed counter elements)
                            // refInfoPerRes[refResNo][1] : reference response elements array
                            refInfoPerRes[refResNo] = [[counter], {}];
                            refInfoPerRes[refResNo][1][resNo] = resParent;
                        } else {
                            // when response is not found
                            refInfoPerRes[refResNo] = null;
                        }
                    }
                });
            }
        });
        RefRes.updateCounterAndIndentedBlockDisplayState();
    });
})();

// バグがあるのでコメントアウト、cが定義されていない
var ReadUpToHere = new (function () {
    // fadeout animation time of operation result display change
    var FADEOUT_ANIMATION_TIME = 150;

    // fetch configuration
    var config = c('UmVhZFVwVG9IZXJl'); // 'UmVhZFVwVG9IZXJl' == 'ReadUpToHere'(Base64Encode)

    // onLoad event initialization variable declaration
    var post_data = {};
    var readup_here_elements;
    var readup_here_op_result_elements;

    /**
     * Add ReadUp To Here Record Ajax Function
     */
    var add_readup_record = function (event) {
        readup_here_elements.off('click').click(function (event) {
            event.preventDefault();
        });
        readup_here_op_result_elements.fadeOut(FADEOUT_ANIMATION_TIME);
        $.ajax({
            cache: false,
            contentType: 'application/json; charset=UTF-8',
            data: post_data,
            error: function (jqXHR, textStatus, errorThrown) {
                if (readup_here_op_result_elements.length > 0) {
                    var replace_html;
                    if (errorThrown === 'Forbidden') {
                        replace_html = '&lt;<a href="' + config.not_login_error_link_url + '">書込ID</a>を発行していません&gt;';
                    } else {
                        replace_html = '&lt;履歴に追加できませんでした&gt;';
                    }
                    if (readup_here_op_result_elements.is(':hidden')) {
                        readup_here_op_result_elements.html(replace_html).show();
                        readup_here_elements.off('click').click(add_readup_record);
                    } else {
                        readup_here_op_result_elements.fadeOut(FADEOUT_ANIMATION_TIME, function () {
                            $(this).html(replace_html).show();
                            readup_here_elements.off('click').click(add_readup_record);
                        })
                    }
                }
            },
            method: 'POST',
            success: function (data, textStatus, jqXHR) {
                if (readup_here_op_result_elements.length > 0) {
                    var replace_html = '&lt;<a href="' + config.history_url + '">履歴</a>に追加しました&gt;';
                    if (readup_here_op_result_elements.is(':hidden')) {
                        readup_here_op_result_elements.html(replace_html).show();
                        readup_here_elements.off('click').click(add_readup_record);
                    } else {
                        readup_here_op_result_elements.fadeOut(FADEOUT_ANIMATION_TIME, function () {
                            $(this).html(replace_html).show();
                            readup_here_elements.off('click').click(add_readup_record);
                        })
                    }
                }
            },
            url: config.endpoint_url
        });
        event.preventDefault(); // Suppress moving by "a" tag
    };

    /**
     * onLoad Event
     */
    $(function () {
        // fetch related html elements (jQuery object)
        readup_here_elements = $('.readup_here');
        readup_here_op_result_elements = $('.readup_here_op_result');

        // setup send thread information
        var send_thread_info = {};
        send_thread_info['mode'] = 'readup_to_here';
        send_thread_info['thread_no'] = readup_here_elements.first().attr('data-threadno');
        post_data['payload'] = JSON.stringify(send_thread_info);

        // add click event
        readup_here_elements.click(add_readup_record).show();
	$('<a name="last_res"></a>').insertBefore($('.res_poster_id').last());
    });
})();

$(function() {
    var no = location.search.replace(/.*no=([0-9]+).*$/, '$1');

    // モーダルを表示する
    $(document).on('mouseover', 'div.comment a.scroll', function(e) {
        if($(this).parents('div.modal').length === 0) {
            var i = 1;
        } else {
            var i = parseInt($(this).parents('div.modal').attr('id').replace('modal', '')) + 1;
        }
	var threadid=$(this).attr('name'), that=$(this);
	var showPopup=function(html){
                    $('div#modal' + i).html(html.replace(/<a (name|id)="[^"]+"><\/a>/g,''));
   		    if(document.getElementById(that.attr('name'))==null){
			$('#modal'+i+' .res_poster_id>.hatugen_blue').remove();
			$('#modal'+i+' .res_poster_id>.hatugen_red').remove();
		    }else if ($("#modal"+i+" .hatugen_blue").size()+$("#modal"+i+" .hatugen_red").size()===0){
			$('#modal'+i+' .res_poster_id').append($('#'+that.attr('name')+' .res_poster_id>.hatugen_blue').clone());
			$('#modal'+i+' .res_poster_id').append($('#'+that.attr('name')+' .res_poster_id>.hatugen_red').clone());
		    }
                    $('div#modal' + i).css({'left': that.offset().left + 'px', 'top' : that.offset().top + that.height() +'px'});
                    $('div#modal' + i).show();
	}
        $('div#modal').append('<div id="modal' + i + '" class="modal"></div>');
	if($('#'+that.attr('name')).html()){
		showPopup($('#'+that.attr('name')).html().replace(/class="refRes"/,'style="display:none"').replace(/<span class="hi_sanshou">[^<]+<\/span>/,""));
	}else
        $.ajax({
            type: "GET",
            url: './read.cgi?l=1-' + '&no=' + no,
	    contentType: 'text/html; charset=Shift_JIS',
            success: function(data){
                if(data.match('<h3>記事が見当たりません</h3>') === null && data.match('<h3>ERROR !</h3>') === null) {
                    var doc = $(data).find("#"+threadid);
		    doc.find('a[id]').first().remove();
		    doc.find('a[name]').first().remove();
		    var html = doc.html();
		    if(!html)
showPopup("<h2>このスレは存在しません</h2>");
else			showPopup(html.replace(/<span class="hatugen_(blue|red)">[^<]+<\/span>/,""));
                }else
showPopup("<h2>このスレは存在しません</h2>");
            }
        });
    });

    $
    // モーダルを隠す
    $(document).on('mousemove', function(e) {
	if(e.target.tagName!=='A'){
		if($(e.target).closest('.modal').size()===0){
			$('.modal').remove();
		}else{
			var cnum = $(e.target).closest('.modal').attr('id');
			$('.modal').each(function(){
				if($(this).attr('id')>cnum) $(this).remove();
			});
		}
	}
    });

    // IDクリックによる背景色の変更
    $(document).on('click', 'span.res_poster_id', function() {
        if($(this).closest('div').css('background-color') === 'rgb(207, 225, 243)' || $(this).closest('div').find('span.hatugen_blue, span.hatugen_red').length === 0) {
            var color = '#f0f0f0';
        } else {
            var color = '#cfe1f3';
        }
        var id = $(this).html().replace(/<.*/,'');
        $('span.res_poster_id').each(function(i, data) {
            if($(data).html().replace(/<.*/,'') === id) {
                $(data).closest('div').css('background-color', color);
            } else {
                $(data).closest('div').css('background-color', '#f0f0f0');
            }
        });
    });
});
