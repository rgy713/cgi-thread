/*
 * Detect Private Browsing Mode
 */

// onLoad
$(function () {
    var private_mode_input_element = $("input[type='hidden'][name='pm']");
    if (private_mode_input_element.length == 1) {
        /*
         * define detect private browsing mode function
         *
         * http://please-sleep.cou929.nu/detect-private-browsing-mode.html
         * https://gist.github.com/cou929/7973956#file-detect-private-browsing-js
         */
        var detectPrivateMode = function (callback) {
            var retry = function (isDone, next) {
                var current_trial = 0, max_retry = 50, interval = 10, is_timeout = false;
                var id = window.setInterval(
                    function () {
                        if (isDone()) {
                            window.clearInterval(id);
                            next(is_timeout);
                        }
                        if (current_trial++ > max_retry) {
                            window.clearInterval(id);
                            is_timeout = true;
                            next(is_timeout);
                        }
                    },
                    interval
                );
            };

            var isIE10OrLater = function (user_agent) {
                var ua = user_agent.toLowerCase();
                if (ua.indexOf('msie') === 0 && ua.indexOf('trident') === 0) {
                    return false;
                }
                var match = /(?:msie|rv:)\s?([\d\.]+)/.exec(ua);
                if (match && parseInt(match[1], 10) >= 10) {
                    return true;
                }
                return false;
            };

            var is_private;

            if (window.webkitRequestFileSystem) {
                window.webkitRequestFileSystem(
                    window.TEMPORARY, 1,
                    function () {
                        is_private = false;
                    },
                    function (e) {
                        console.log(e);
                        is_private = true;
                    }
                );
            } else if (window.indexedDB && /Firefox/.test(window.navigator.userAgent)) {
                var db;
                try {
                    db = window.indexedDB.open('test');
                } catch (e) {
                    is_private = true;
                }

                if (typeof is_private === 'undefined') {
                    retry(
                        function isDone() {
                            return db.readyState === 'done' ? true : false;
                        },
                        function next(is_timeout) {
                            if (!is_timeout) {
                                is_private = db.result ? false : true;
                            }
                        }
                    );
                }
            } else if (isIE10OrLater(window.navigator.userAgent)) {
                is_private = false;
                try {
                    if (!window.indexedDB) {
                        is_private = true;
                    }
                } catch (e) {
                    is_private = true;
                }
            } else if (window.localStorage && /Safari/.test(window.navigator.userAgent)) {
                try {
                    window.localStorage.setItem('test', 1);
                } catch (e) {
                    is_private = true;
                }

                if (typeof is_private === 'undefined') {
                    is_private = false;
                    window.localStorage.removeItem('test');
                }
            }

            retry(
                function isDone() {
                    return typeof is_private !== 'undefined' ? true : false;
                },
                function next(is_timeout) {
                    callback(is_private, is_timeout);
                }
            );
        }

        // define callback function called from private browsing mode detecting
        detectPrivateMode(function (is_private, is_timeout) {
            if (is_timeout) {
                return;
            }
            if (is_private) {
                private_mode_input_element.val('1');
            } else {
                private_mode_input_element.val('0');
            }
        });
    }
});
