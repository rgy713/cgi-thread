$(function () {
    // fetch configuration
    var config = c('VGhyZWFkTnVtL05hbWVBdXRvUHJvaGliaXRpbmc='); // 'VGhyZWFkTnVtL05hbWVBdXRvUHJvaGliaXRpbmc=' == 'ThreadNum/NameAutoProhibiting'(Base64Encode)

    // define ajax execution function
    function execute_ajax(post_data, message_elements, result_span) {
        var success_message = "実行しました。";
        var error_message = "実行できませんでした。";

        message_elements.hide();
        if (post_data !== null) {
            $.ajax({
                cache: false,
                contentType: 'application/json; charset=UTF-8',
                data: post_data,
                error: function (jqXHR, textStatus, errorThrown) {
                    result_span.text(error_message).show();
                },
                method: 'POST',
                success: function (data, textStatus, jqXHR) {
                    result_span.text(success_message).show();
                },
                url: config.endpoint_url
            });
        } else {
            result_span.text(error_message).show();
        }
    }


    // Add ClickEvent(Ajax) to Thread Number Prohibit Links
    var THREAD_NUMBER_PROHIBIT_TIME_1_LINK = $("#thread_num_prohibit_time_1");
    var THREAD_NUMBER_PROHIBIT_TIME_2_LINK = $("#thread_num_prohibit_time_2");
    var THREAD_NUMBER_PROHIBIT_TIME_3_LINK = $("#thread_num_prohibit_time_3");
    var THREAD_NUMBER_PROHIBIT_TIME_4_LINK = $("#thread_num_prohibit_time_4");
    var THREAD_NUMBER_PROHIBIT_TIME_5_LINK = $("#thread_num_prohibit_time_5");
    var THREAD_NUMBER_PROHIBIT_TIME_6_LINK = $("#thread_num_prohibit_time_6");
    var THREAD_NUMBER_PROHIBIT_PERMANENT_LINK = $("#thread_num_prohibit_permanent");
    var THREAD_NUMBER_PROHIBIT_REMOVE_LINK = $("#thread_num_prohibit_remove");
    var THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES = $(".thread_num_prohibit_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_1_AJAX_MESSAGE = $("#thread_num_prohibit_time_1_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_2_AJAX_MESSAGE = $("#thread_num_prohibit_time_2_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_3_AJAX_MESSAGE = $("#thread_num_prohibit_time_3_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_4_AJAX_MESSAGE = $("#thread_num_prohibit_time_4_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_5_AJAX_MESSAGE = $("#thread_num_prohibit_time_5_ajax_message");
    var THREAD_NUMBER_PROHIBIT_TIME_6_AJAX_MESSAGE = $("#thread_num_prohibit_time_6_ajax_message");
    var THREAD_NUMBER_PROHIBIT_PERMANENT_AJAX_MESSAGE = $("#thread_num_prohibit_permanent_ajax_message");
    var THREAD_NUMBER_PROHIBIT_REMOVE_AJAX_MESSAGE = $("#thread_num_prohibit_remove_ajax_message");

    function _create_thread_num_prohibit_post_data(thread_num, action) {
        var send_data = {};
        send_data["mode"] = "thread_num_auto_prohibiting";
        send_data["thread_number"] = parseInt(thread_num);
        send_data["action"] = action;

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    THREAD_NUMBER_PROHIBIT_TIME_1_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_1"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_1_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_TIME_2_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_2"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_2_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_TIME_3_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_3"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_3_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_TIME_4_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_4"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_4_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_TIME_5_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_5"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_5_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_TIME_6_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_6"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_TIME_6_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_PERMANENT_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "add_permanently"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_PERMANENT_AJAX_MESSAGE
        );
        return false;
    });
    THREAD_NUMBER_PROHIBIT_REMOVE_LINK.click(function () {
        execute_ajax(
            _create_thread_num_prohibit_post_data($(this).attr("thread_num"), "remove"),
            THREAD_NUMBER_PROHIBIT_AJAX_MESSAGES,
            THREAD_NUMBER_PROHIBIT_REMOVE_AJAX_MESSAGE
        );
        return false;
    });


    // Add ClickEvent(Ajax) to Thread Title Prohibit Links
    var THREAD_TITLE_PROHIBIT_TIME_1_LINKS = $(".thread_title_prohibit_time_1");
    var THREAD_TITLE_PROHIBIT_TIME_2_LINKS = $(".thread_title_prohibit_time_2");
    var THREAD_TITLE_PROHIBIT_TIME_3_LINKS = $(".thread_title_prohibit_time_3");
    var THREAD_TITLE_PROHIBIT_TIME_4_LINKS = $(".thread_title_prohibit_time_4");
    var THREAD_TITLE_PROHIBIT_TIME_5_LINKS = $(".thread_title_prohibit_time_5");
    var THREAD_TITLE_PROHIBIT_TIME_6_LINKS = $(".thread_title_prohibit_time_6");
    var THREAD_TITLE_PROHIBIT_PERMANENT_LINKS = $(".thread_title_prohibit_permanent");
    var THREAD_TITLE_PROHIBIT_REMOVE_LINKS = $(".thread_title_prohibit_remove");
    var THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_1_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_1_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_2_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_2_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_3_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_3_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_4_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_4_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_5_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_5_ajax_message";
    var THREAD_TITLE_PROHIBIT_TIME_6_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_time_6_ajax_message";
    var THREAD_TITLE_PROHIBIT_PERMANENT_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_permanent_ajax_message";
    var THREAD_TITLE_PROHIBIT_REMOVE_AJAX_MESSAGE_CLASS_NAME = "thread_title_prohibit_remove_ajax_message";

    function _create_thread_title_prohibit_post_data(action, thread_title, word_type) {
        var send_data = {};
        send_data["mode"] = "thread_title_auto_prohibiting";
        send_data["action"] = action;
        send_data["thread_title"] = thread_title;
        send_data["word_type"] = parseInt(word_type);

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    THREAD_TITLE_PROHIBIT_TIME_1_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_1", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_1_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_TIME_2_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_2", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_2_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_TIME_3_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_3", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_3_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_TIME_4_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_4", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_4_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_TIME_5_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_5", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_5_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_TIME_6_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_6", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_TIME_6_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_PERMANENT_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("add_permanently", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_PERMANENT_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });
    THREAD_TITLE_PROHIBIT_REMOVE_LINKS.click(function () {
        execute_ajax(
            _create_thread_title_prohibit_post_data("remove", $(this).attr("thread_title"), $(this).attr("word_type")),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_AJAX_MESSAGE_CLASS_NAME),
            $(this).siblings("." + THREAD_TITLE_PROHIBIT_REMOVE_AJAX_MESSAGE_CLASS_NAME)
        );
        return false;
    });


    // define restrict user common targets
    var COMMON_RESTRICT_USER_TARGETS = ["cookie_a", "history_id", "host", "user_id"];


    // Add ClickEvent(Ajax) to Restrict User Links
    var RESTRICT_USER_TIME_1_LINKS = $(".restrict_user_time_1");
    var RESTRICT_USER_TIME_2_LINKS = $(".restrict_user_time_2");
    var RESTRICT_USER_TIME_3_LINKS = $(".restrict_user_time_3");
    var RESTRICT_USER_TIME_4_LINKS = $(".restrict_user_time_4");
    var RESTRICT_USER_TIME_5_LINKS = $(".restrict_user_time_5");
    var RESTRICT_USER_TIME_6_LINKS = $(".restrict_user_time_6");
    var RESTRICT_USER_TIME_7_LINKS = $(".restrict_user_time_7");
    var RESTRICT_USER_PERMANENT_LINKS = $(".restrict_user_permanent");
    var RESTRICT_USER_REMOVE_LINKS = $(".restrict_user_remove");
    var RESTRICT_USER_AJAX_MESSAGES_CLASSNAME = "restrict_user_ajax_message";
    var RESTRICT_USER_TIME_1_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_1_ajax_message";
    var RESTRICT_USER_TIME_2_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_2_ajax_message";
    var RESTRICT_USER_TIME_3_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_3_ajax_message";
    var RESTRICT_USER_TIME_4_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_4_ajax_message";
    var RESTRICT_USER_TIME_5_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_5_ajax_message";
    var RESTRICT_USER_TIME_6_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_6_ajax_message";
    var RESTRICT_USER_TIME_7_AJAX_MESSAGE_CLASSNAME = "restrict_user_time_7_ajax_message";
    var RESTRICT_USER_PERMANENT_AJAX_MESSAGE_CLASSNAME = "restrict_user_permanent_ajax_message";
    var RESTRICT_USER_REMOVE_AJAX_MESSAGE_CLASSNAME = "restrict_user_remove_ajax_message";

    function _create_restrict_user_post_data(click_element, action) {
        var jquery_click_element = $(click_element);
        var send_data = {};
        send_data["mode"] = "restrict_user_from_thread_page";
        send_data["action"] = action;
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = jquery_click_element.attr(attr_name);
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    RESTRICT_USER_TIME_1_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_1"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_1_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_TIME_2_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_2"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_2_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_TIME_3_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_3"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_3_AJAX_MESSAGE_CLASSNAME)
        );
        return false;        
    });
    RESTRICT_USER_TIME_4_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_4"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_4_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_TIME_5_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_5"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_5_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_TIME_6_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_6"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_6_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_TIME_7_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_7"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_TIME_7_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_PERMANENT_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "add_permanently"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_PERMANENT_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_REMOVE_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_post_data(this, "remove"),
            $(this).siblings("." + RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_REMOVE_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });


    // Add ClickEvent(Ajax) to Restrict User By Time Range Links
    var RESTRICT_USER_BY_TIME_RANGE_TIME_1_LINKS = $(".restrict_user_by_time_range_time_1");
    var RESTRICT_USER_BY_TIME_RANGE_TIME_2_LINKS = $(".restrict_user_by_time_range_time_2");
    var RESTRICT_USER_BY_TIME_RANGE_TIME_3_LINKS = $(".restrict_user_by_time_range_time_3");
    var RESTRICT_USER_BY_TIME_RANGE_TIME_4_LINKS = $(".restrict_user_by_time_range_time_4");
    var RESTRICT_USER_BY_TIME_RANGE_PERMANENT_LINKS = $(".restrict_user_by_time_range_permanent");
    var RESTRICT_USER_BY_TIME_RANGE_REMOVE_LINKS = $(".restrict_user_by_time_range_remove");
    var RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME = "restrict_user_by_time_range_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_TIME_1_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_time_1_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_TIME_2_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_time_2_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_TIME_3_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_time_3_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_TIME_4_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_time_4_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_PERMANENT_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_permanent_ajax_message";
    var RESTRICT_USER_BY_TIME_RANGE_REMOVE_AJAX_MESSAGE_CLASSNAME = "restrict_user_by_time_range_remove_ajax_message";

    function _create_restrict_user_by_time_range_post_data(click_element, action) {
        var jquery_click_element = $(click_element);
        var send_data = {};
        send_data["mode"] = "restrict_user_from_thread_page_by_time_range";
        send_data["action"] = action;
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = jquery_click_element.attr(attr_name);
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    RESTRICT_USER_BY_TIME_RANGE_TIME_1_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "add_1"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_TIME_1_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_BY_TIME_RANGE_TIME_2_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "add_2"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_TIME_2_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_BY_TIME_RANGE_TIME_3_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "add_3"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_TIME_3_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_BY_TIME_RANGE_TIME_4_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "add_4"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_TIME_4_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_BY_TIME_RANGE_PERMANENT_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "add_permanently"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_PERMANENT_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    RESTRICT_USER_BY_TIME_RANGE_REMOVE_LINKS.click(function () {
        execute_ajax(
            _create_restrict_user_by_time_range_post_data(this, "remove"),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + RESTRICT_USER_BY_TIME_RANGE_REMOVE_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });


    // Add ClickEvent(Ajax) to In Thread Only Restrict User Links
    var IN_THREAD_ONLY_RESTRICT_USER_TIME_LINKS = $(".in_thread_only_restrict_user_time");
    var IN_THREAD_ONLY_RESTRICT_USER_REMOVE_LINKS = $(".in_thread_only_restrict_user_remove");
    var IN_THREAD_ONLY_RESTRICT_USER_AJAX_MESSAGES_CLASSNAME = "in_thread_only_restrict_user_ajax_message";
    var IN_THREAD_ONLY_RESTRICT_USER_TIME_AJAX_MESSAGE_CLASSNAME = "in_thread_only_restrict_user_time_ajax_message";
    var IN_THREAD_ONLY_RESTRICT_USER_REMOVE_AJAX_MESSAGE_CLASSNAME = "in_thread_only_restrict_user_remove_ajax_message";

    function _create_in_thread_only_restrict_user_post_data(click_element, action) {
        var jquery_click_element = $(click_element);
        var send_data = {};
        send_data["mode"] = "in_thread_only_restrict_user_from_thread_page";
        send_data["action"] = action;
        send_data["thread_number"] = parseInt(jquery_click_element.attr("thread_num"));
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = jquery_click_element.attr(attr_name);
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    IN_THREAD_ONLY_RESTRICT_USER_TIME_LINKS.click(function () {
        execute_ajax(
            _create_in_thread_only_restrict_user_post_data(this, "add"),
            $(this).siblings("." + IN_THREAD_ONLY_RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + IN_THREAD_ONLY_RESTRICT_USER_TIME_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });
    IN_THREAD_ONLY_RESTRICT_USER_REMOVE_LINKS.click(function () {
        execute_ajax(
            _create_in_thread_only_restrict_user_post_data(this, "remove"),
            $(this).siblings("." + IN_THREAD_ONLY_RESTRICT_USER_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + IN_THREAD_ONLY_RESTRICT_USER_REMOVE_AJAX_MESSAGE_CLASSNAME)
        );
        return false;
    });


    // Add ClickEvent(Ajax) to Highlight User Info Buttons/Links
    var HIGHLIGHT_USERINFO_ADD_BUTTONS = $(".highlight_userinfo_add");
    var HIGHLIGHT_USERINFO_REMOVE_LINKS = $(".highlight_userinfo_remove");
    var HIGHLIGHT_USERINFO_COLOR_SELECT_CLASSNAME = "highlight_userinfo_color";
    var HIGHLIGHT_USERINFO_AJAX_MESSAGES_CLASSNAME = "highlight_userinfo_ajax_message";
    var HIGHLIGHT_USERINFO_ADD_AJAX_MESSAGES_CLASSNAME = "highlight_userinfo_add_ajax_message";
    var HIGHLIGHT_USERINFO_REMOVE_AJAX_MESSAGES_CLASSNAME = "highlight_userinfo_remove_ajax_message";

    function _create_highlight_userinfo_post_data(click_element, action) {
        var jquery_click_element = $(click_element);
        var send_data = {};
        send_data["mode"] = "highlight_userinfo";
        send_data["action"] = action;

        if (action === "add") {
            send_data["color"] = parseInt(jquery_click_element.siblings("." + HIGHLIGHT_USERINFO_COLOR_SELECT_CLASSNAME).val())
        }

        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = jquery_click_element.attr(attr_name);
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    HIGHLIGHT_USERINFO_ADD_BUTTONS.click(function () {
        execute_ajax(
            _create_highlight_userinfo_post_data(this, "add"),
            $(this).siblings("." + HIGHLIGHT_USERINFO_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + HIGHLIGHT_USERINFO_ADD_AJAX_MESSAGES_CLASSNAME)
        );
        return false;
    });
    HIGHLIGHT_USERINFO_REMOVE_LINKS.click(function () {
        execute_ajax(
            _create_highlight_userinfo_post_data(this, "remove"),
            $(this).siblings("." + HIGHLIGHT_USERINFO_AJAX_MESSAGES_CLASSNAME),
            $(this).siblings("." + HIGHLIGHT_USERINFO_REMOVE_AJAX_MESSAGES_CLASSNAME)
        );
        return false;
    });


    // Add Restrict User Form RegistButton ClickEvent(Ajax)
    function _create_restrict_user_regist_post_data_from_form(restrict_userinfo, add_type) {
        var send_data = {};
        send_data["mode"] = "restrict_user_from_form";
        send_data["action"] = "add_" + add_type;
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = restrict_userinfo[attr_name];
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        if (Object.keys(send_data).length > 2) {
            var post_data = {};
            post_data["payload"] = JSON.stringify(send_data);
            return post_data;
        } else {
            return null;
        }
    }

    // CSV Input Form
    $("#restrict_user_form_csv_regist").click(function () {
        var restrict_userinfo = {};

        // parse CSV and fetch item value
        var csv_item_names = ["cookie_a", "user_id", "history_id", "host"];
        var values = $("#restrict_user_form_csv_values").val().split(",");
        if (values.length === csv_item_names.length) {
            for (var i = 0; i < csv_item_names.length; i++) {
                if (values[i] === "") {
                    continue;
                }
                restrict_userinfo[csv_item_names[i]] = values[i];
            }
        }

        // create post data and execute Ajax
        var add_type = $("#restrict_user_form_csv_type").val();
        var result_span = $("#restrict_user_form_csv_ajax_message");
        execute_ajax(
            _create_restrict_user_regist_post_data_from_form(restrict_userinfo, add_type),
            result_span,
            result_span
        );
        return false;
    });

    // Individual Input Form
    $("#restrict_user_form_individual_regist").click(function () {
        var restrict_userinfo = {};

        // fetch item value
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var item_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = $("#restrict_user_form_individual_" + item_name).val();
            if (value === "") {
                continue;
            }
            restrict_userinfo[item_name] = value;
        }

        // create post data and execute Ajax
        var add_type = $("#restrict_user_form_individual_type").val();
        var result_span = $("#restrict_user_form_individual_ajax_message");
        execute_ajax(
            _create_restrict_user_regist_post_data_from_form(restrict_userinfo, add_type),
            result_span,
            result_span
        );
        return false;
    });


    // Add Highlight User Info RegistButton ClickEvent(Ajax)
    function _create_highlight_userinfo_regist_post_data_from_form(highlight_userinfo, color) {
        var send_data = {};
        send_data["mode"] = "highlight_userinfo_from_form";
        send_data["action"] = "add";
        send_data["color"] = parseInt(color);

        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var attr_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = highlight_userinfo[attr_name];
            if (value === void 0) {
                continue;
            }
            send_data[attr_name] = value;
        }

        if (Object.keys(send_data).length > 3) {
            var post_data = {};
            post_data["payload"] = JSON.stringify(send_data);
            return post_data;
        } else {
            return null;
        }
    }

    // CSV Input Form
    $("#highlight_userinfo_form_csv_regist").click(function () {
        var highlight_userinfo = {};

        // parse CSV and fetch item value
        var csv_item_names = ["cookie_a", "user_id", "history_id", "host"];
        var values = $("#highlight_userinfo_form_csv_values").val().split(",");
        if (values.length === csv_item_names.length) {
            for (var i = 0; i < csv_item_names.length; i++) {
                if (values[i] === "") {
                    continue;
                }
                highlight_userinfo[csv_item_names[i]] = values[i];
            }
        }

        // create post data and execute Ajax
        var color = $("#highlight_userinfo_form_csv_color").val();
        var result_span = $("#highlight_userinfo_form_csv_ajax_message");
        execute_ajax(
            _create_highlight_userinfo_regist_post_data_from_form(highlight_userinfo, color),
            result_span,
            result_span
        );
        return false;
    });

    // Individual Input Form
    $("#highlight_userinfo_form_individual_regist").click(function () {
        var highlight_userinfo = {};

        // fetch item value
        for (var i = 0; i < COMMON_RESTRICT_USER_TARGETS.length; i++) {
            var item_name = COMMON_RESTRICT_USER_TARGETS[i];
            var value = $("#highlight_userinfo_form_individual_" + item_name).val();
            if (value === "") {
                continue;
            }
            highlight_userinfo[item_name] = value;
        }

        // create post data and execute Ajax
        var color = $("#highlight_userinfo_form_individual_color").val();
        var result_span = $("#highlight_userinfo_form_individual_ajax_message");
        execute_ajax(
            _create_highlight_userinfo_regist_post_data_from_form(highlight_userinfo, color),
            result_span,
            result_span
        );
        return false;
    });


    // Add Highlight UserAgent Form Buttons ClickEvent(Ajax)
    var HIGHLIGHT_UA_FORM_CURRENT_SETTINGS_AJAX_MESSAGE_ELEMENTS = $(".highlight_ua_form_current_settings_ajax_messages");
    function _create_highlight_useragent_post_data_from_form(action, host, useragent, opt_color) {
        var send_data = {};
        send_data["mode"] = "highlight_ua_from_form";
        send_data["action"] = action;

        if (host === "" || useragent === "") {
            return null;
        }
        send_data["host"] = host;
        send_data["useragent"] = useragent;

        if (action === "add") {
            if (opt_color !== void 0) {
                send_data["color"] = parseInt(opt_color);
            } else {
                return null;
            }
        }

        var post_data = {};
        post_data["payload"] = JSON.stringify(send_data);
        return post_data;
    }

    // Regist Form
    $("#highlight_ua_form_regist").click(function () {
        var host = $("#highlight_ua_form_regist_host").val();
        var useragent = $("#highlight_ua_form_regist_useragent").val();
        var color = $("#highlight_ua_form_regist_color").val();

        // create post data and execute Ajax
        var result_span = $("#highlight_ua_form_regist_ajax_message");
        execute_ajax(
            _create_highlight_useragent_post_data_from_form("add", host, useragent, color),
            result_span,
            result_span
        );
        return false;
    });

    // CurrentSettings Timestamp Update
    $("#highlight_ua_form_current_settings_update_timestamp").click(function () {
        var selected_setting = $("#highlight_ua_form_current_settings").children("option").filter(":selected");
        var host = selected_setting.attr("data-host");
        var useragent = selected_setting.attr("data-useragent");

        // create post data and execute Ajax
        execute_ajax(
            _create_highlight_useragent_post_data_from_form("update_timestamp", host, useragent),
            HIGHLIGHT_UA_FORM_CURRENT_SETTINGS_AJAX_MESSAGE_ELEMENTS,
            $("#highlight_ua_form_current_settings_update_timestamp_ajax_message")
        );
        return false;
    });

    // CurrentSettings Timestamp Update
    $("#highlight_ua_form_current_settings_remove").click(function () {
        var selected_setting = $("#highlight_ua_form_current_settings").children("option").filter(":selected");
        var host = selected_setting.attr("data-host");
        var useragent = selected_setting.attr("data-useragent");

        // create post data and execute Ajax
        execute_ajax(
            _create_highlight_useragent_post_data_from_form("remove", host, useragent),
            HIGHLIGHT_UA_FORM_CURRENT_SETTINGS_AJAX_MESSAGE_ELEMENTS,
            $("#highlight_ua_form_current_settings_remove_ajax_message")
        );
        return false;
    });
});
