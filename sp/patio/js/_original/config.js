/**
 * Return function configures
 *
 * @param function_name
 * @returns {*}
 * @export
 */
var c = function (function_name) {
    if (function_name === 'TkdJRA==') { // 'TkdJRA==' == 'NGID'(Base64Encode)
        return {
            ngres_message: '', // "${ngres_comment}"
            chain_ng: true, // "(${chain_ng}?'true':'false')"
            use_ngid: true, // "(($ngid&&$idkey)?'true':'false')"
            ngid_cookie_limit_reached_error_message: '', // "${ngid_error_message}"
            use_ngname: true, // "($ngname?'true':'false')"
            ngname_cookie_limit_reached_error_message: '', // "${ngname_error_message}"
            ngname_display_characters: 0, // ${ngname_dispchar_length}
            cookie_current_dirpath: '' // "${cookie_current_dirpath}"
        };
    } else if (function_name === 'UmVmUmVz') { // 'UmVmUmVz' == 'RefRes'(Base64Encode)
        return {
            ngres_hide_reference_counter: true, // "($ngres_hide_refcounter?'true':'false')"
            number_of_anchor_made_ref_count_exempt: 0 // ${number_of_anchor_made_ref_count_exempt}
        };
    } else if (function_name === 'UmVhZFVwVG9IZXJl') { // 'UmVhZFVwVG9IZXJl' == 'ReadUpToHere'(Base64Encode)
        return {
            endpoint_url: '', // $readapicgi
            history_url: '', // $readup_to_here_added_history_link_url
            not_login_error_link_url: '', // $readup_to_here_not_login_error_link_url
        };
    } else if (function_name === 'VGhyZWFkTnVtL05hbWVBdXRvUHJvaGliaXRpbmc=') { // 'VGhyZWFkTnVtL05hbWVBdXRvUHJvaGliaXRpbmc=' == 'ThreadNum/NameAutoProhibiting' (Base64Encode)
        return {
            endpoint_url: '' // $readapicgi
        };
    }
};
