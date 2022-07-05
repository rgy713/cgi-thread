#!/usr/bin/perl

#-------------------------------------#
# WebPatio 禁止条件上書き設定ファイル #
#-------------------------------------#

#-------------------------------------------------
#  ◎重複投稿処理
#-------------------------------------------------

# 重複投稿処理の対象とするスレッド名を設定します
# スレッド名の指定文字列の先頭に「!」を追加した場合は、
# 設定に一致しないものを対象とします。
#
@duplicate_post_restrict_thread = (
);

#-------------------------------------------------
#  ◎名前欄非表示機能
#-------------------------------------------------

# 名前欄を非表示にするスレッドのスレッド名を
# 「,」区切りで設定します
@hide_form_name_field = (
);

#-------------------------------------------------
#  ◎投稿時の名前の消去機能
#-------------------------------------------------
#
# 投稿時に名前を消去する対象の投稿を
# 'スレッド名:名前:ホスト<>UserAgent:CookieA or 登録ID or 書込ID' のリストで設定します
#
# スレッド名・名前・ホスト名・UserAgentは部分一致、CookieA or 登録IDは完全一致で判定を行います
#
# スレッド名の指定文字列の先頭に「!」を追加した場合は、
# 設定に一致しないものを対象とします。
#
# 名前に、「◆hogehoge」などで「◆」を含む場合は、トリップ変換後の名前で一致判定を行います
# また、「#hogehoge」などで「#」を含む場合は、トリップ変換の名前で一致判定を行います
#
# ホスト名とUserAgentの組み合わせ・CookieA or 登録ID・書込IDの指定文字列では、
# 何も記述しなかった場合や「-」のみを設定した場合は、その項目について判定を行いません。
# また、指定文字列の先頭に「!」を追加した場合は、設定に一致しないものを対象とします。
#
# ホスト名とUserAgentの組み合わせの指定文字列では、
# ホスト名とUserAgentを「<>」で区切って記述しますが、
# 「<>」が含まれない場合は、ホスト名として認識し、全てのUserAgentに一致します。
# また、ホスト名とUserAgentの組み合わせ指定を「●」で区切ると、
# それぞれの指定のいずれかに一致した場合に対象として判定します。
#
# その他、スレッド名・名前・ホスト名とUserAgentの組み合わせの設定フォーマットについて、
# 自動書き込み禁止機能と同様となります
#
@remove_name_on_post = (
);


# 禁止ワード
# → 投稿時禁止するワードをコンマで区切る
$no_wd = '';


# 名前欄NGワード機能(禁止文字列チェック)
# 名前欄で入力を禁止する文字列を半角カンマ区切りで指定します
$ng_nm = "";


# 名前欄NGワード機能(入力許可文字チェック)
# 名前欄で入力を許可する文字をUnicode文字コード正規表現で指定します
# 正規表現は必ずダブルクオーテーションで囲んで指定して下さい
# ほか、トリップ作成識別子「#」は、プログラム側で追加しています
#
# また、1つも指定しない場合(@permit_name_regex = ();)は
# 入力許可文字のチェックを行いません
# =====================================================
# Unicode 文字コード正規表現例
# =====================================================
# 半角数字: \N{U+0030}-\N{U+0039}
# 全角数字: \N{U+FF10}-\N{U+FF19}
# 半角英字: \N{U+0041}-\N{U+005A}\N{U+0061}-\N{U+007A}
# 全角英字: \N{U+FF21}-\N{U+FF3A}\N{U+FF41}-\N{U+FF5A}
# ひらがな: \N{U+3041}-\N{U+3096}
# 半角カタカナ: \N{U+FF66}-\N{U+FF6F}\N{U+FF71}-\N{U+FF9D}
# 全角カタカナ: \N{U+30A1}-\N{U+30FA}
# 漢字: \\p{Han}
# 結合用濁点・半濁点: \N{U+3099}\N{U+309A}
# 半角独立濁点・半濁点(ﾞおよびﾟ): \N{U+FF9E}\N{U+FF9F}
# 全角独立濁点・半濁点(゛および゜): \N{U+309B}\N{U+309C}
# 半角スペース( ): \N{U+0020}
# 全角スペース(　): \N{U+3000}
# 半角感嘆符(!): \N{U+0021}
# 全角感嘆符(！): \N{U+FF01}
# 半角句読点(､および｡): \N{U+FF64}\N{U+FF61}
# 全角句読点(、および。): \N{U+3001}\N{U+3002}
# 半角中点(･): \N{U+FF65}
# 全角中点(・): \N{U+30FB}
# 半角長音(ｰ): \N{U+FF70}
# 全角長音(ー): \N{U+30FC}
# ハイフンマイナス(-): \\\N{U+002D}
# 半角プラス(+): \N{U+002B}
# 全角プラス(＋): \N{U+FF0B}
# 半角ピリオド(.): \N{U+002E}
# 全角ピリオド(．): \N{U+FF0E}
# 半角等号(=): \N{U+003D}
# 全角等号(＝): \N{U+FF1D}
# =====================================================
@permit_name_regex = (
    "\N{U+0030}-\N{U+0039}", # 半角数字
    "\N{U+FF10}-\N{U+FF19}", # 全角数字
    "\N{U+0041}-\N{U+005A}\N{U+0061}-\N{U+007A}", # 半角英字
    "\N{U+FF21}-\N{U+FF3A}\N{U+FF41}-\N{U+FF5A}", # 全角英字
    "\N{U+3041}-\N{U+3096}", # ひらがな
    "\N{U+FF66}-\N{U+FF6F}\N{U+FF71}-\N{U+FF9D}", # 半角カタカナ
    "\N{U+30A1}-\N{U+30FA}", # 全角カタカナ
    "\\p{Han}", # 漢字
    "\N{U+3099}\N{U+309A}", # 結合用濁点・半濁点
    "\N{U+FF9E}\N{U+FF9F}", # 半角独立濁点・半濁点
    "\N{U+309B}\N{U+309C}", # 全角独立濁点・半濁点
    "\N{U+0020}", # 半角スペース
    "\N{U+3000}", # 全角スペース
    "\N{U+0021}", # 半角感嘆符
    "\N{U+FF01}", # 全角感嘆符
    "\N{U+FF64}\N{U+FF61}", # 半角句読点
    "\N{U+3001}\N{U+3002}", # 全角句読点
    "\N{U+FF65}", # 半角中点
    "\N{U+30FB}", # 全角中点
    "\N{U+FF70}", # 半角長音
    "\N{U+30FC}", # 全角長音
    "\\\N{U+002D}", # ハイフンマイナス
    "\N{U+002B}", # 半角プラス
    "\N{U+FF0B}", # 全角プラス
    "\N{U+002E}", # 半角ピリオド
    "\N{U+FF0E}", # 全角ピリオド
    "\N{U+003D}", # 半角等号
    "\N{U+FF1D}" # 全角等号
);


#-------------------------------------------------
#  ◎表示内容分岐機能
#-------------------------------------------------
# スレッドページで表示範囲のレスに設定した文字列を含むか、
# 画像アップチェックが有効（init.cgiで設定）の場合は画像が含まれている場合に、
# 表示内容を変更して出力します

# 表示内容分岐機能 対象文字列設定
@contents_branching_keyword = ();


#-------------------------------------------------
#  ◎アップロード禁止画像指定機能
#-------------------------------------------------

# アップロード禁止画像ファイル MD5ハッシュ値設定
# 禁止画像として検知する、オリジナル画像ファイルのMD5ハッシュ値を設定します
# 入力例: 'd41d8cd98f00b204e9800998ecf8427e',
@prohibit_img_md5hash = (
);


#-------------------------------------------------
#  ◎初回書き込みまでの時間制限機能
#-------------------------------------------------
# 初回書き込みまでの時間制限機能 対象外ユーザー設定
# 制限対象から除外するユーザーを
# 「ホスト<>UserAgent:CookieA or 登録ID or 書込ID」のように指定します
@firstpost_restrict_exempt = (
);

#-------------------------------------------------
#  ◎ホストなどによる画像アップロードの無効
#-------------------------------------------------
# 画像アップロードさせたくないユーザーを
# 'スレッド名:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:メモ欄' のリストで設定します
@disable_img_upload = (
);

#-------------------------------------------------
#  ◎ホストなどによるageの無効
#-------------------------------------------------
# 強制的にsage投稿させるユーザーを
# 'スレッド名:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:メモ欄' のリストで設定します
@disable_age = (
);

#-------------------------------------------------
#  ◎スレッド閲覧制限機能 設定項目
#-------------------------------------------------

# スレッド閲覧制限対象ユーザー
# '無効:スレッド名:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:CookieAの有無:日付による除外:CookieA or 登録ID or 書込IDの除外:メモ欄' のリストで設定します
# (先頭の「無効」のフィールドに ▼ がセットされている設定は、制限対象判定を行いません)
@thread_browsing_restrict_user = (
);

#-------------------------------------------------
#  ◎自動書き込み禁止機能
#-------------------------------------------------

# スレッドタイトル(否定条件)・変換前/変換後画像のMD5・一致時ログ出力コメント・ホスト名とUserAgent・CookieA or 登録ID or 書込IDの組み合わせ
@auto_post_prohibit_combination_imgmd5 = (
);

## スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能 ##

# レス内容 制限単語 (「自動書き込み禁止機能(レス)」のレス内容に相当)
# 制限単語1
$auto_post_prohibit_thread_title_res_target_restrict_keyword = '';

# 制限単語2
$auto_post_prohibit_thread_title_res_target_restrict_keyword_2 = '';

# 制限単語3
$auto_post_prohibit_thread_title_res_target_restrict_keyword_3 = '';

# 制限単語4
$auto_post_prohibit_thread_title_res_target_restrict_keyword_4 = '';

# 制限単語5
$auto_post_prohibit_thread_title_res_target_restrict_keyword_5 = '';

# 制限単語6
$auto_post_prohibit_thread_title_res_target_restrict_keyword_6 = '';

# 制限単語7
$auto_post_prohibit_thread_title_res_target_restrict_keyword_7 = '';

# 制限単語8
$auto_post_prohibit_thread_title_res_target_restrict_keyword_8 = '';

# 制限単語9
$auto_post_prohibit_thread_title_res_target_restrict_keyword_9 = '';

# 制限単語10
$auto_post_prohibit_thread_title_res_target_restrict_keyword_10 = '';

# 制限単語11
$auto_post_prohibit_thread_title_res_target_restrict_keyword_11 = '';

# 制限単語12
$auto_post_prohibit_thread_title_res_target_restrict_keyword_12 = '';

# 制限単語13
$auto_post_prohibit_thread_title_res_target_restrict_keyword_13 = '';

# 制限単語14
$auto_post_prohibit_thread_title_res_target_restrict_keyword_14 = '';

# 制限単語15
$auto_post_prohibit_thread_title_res_target_restrict_keyword_15 = '';

# 制限単語16
$auto_post_prohibit_thread_title_res_target_restrict_keyword_16 = '';

# 制限単語17
$auto_post_prohibit_thread_title_res_target_restrict_keyword_17 = '';

# 制限単語18
$auto_post_prohibit_thread_title_res_target_restrict_keyword_18 = '';

# 制限単語19
$auto_post_prohibit_thread_title_res_target_restrict_keyword_19 = '';

# 制限単語20
$auto_post_prohibit_thread_title_res_target_restrict_keyword_20 = '';

# レス内容 制限除外単語 (制限単語Nと除外単語Nが対応します)
# 除外単語1
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword = '';

# 除外単語2
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_2 = '';

# 除外単語3
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_3 = '';

# 除外単語4
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_4 = '';

# 除外単語5
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_5 = '';

# 除外単語6
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_6 = '';

# 除外単語7
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_7 = '';

# 除外単語8
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_8 = '';

# 除外単語9
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_9 = '';

# 除外単語10
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_10 = '';

# 除外単語11
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_11 = '';

# 除外単語12
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_12 = '';

# 除外単語13
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_13 = '';

# 除外単語14
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_14 = '';

# 除外単語15
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_15 = '';

# 除外単語16
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_16 = '';

# 除外単語17
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_17 = '';

# 除外単語18
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_18 = '';

# 除外単語19
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_19 = '';

# 除外単語20
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_20 = '';

# 複数回投稿時の自動書き込み禁止機能 制限対象設定
# 「無効:スレッド名:レス1の除外単語:制限単語:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:時間指定:メモ欄」のように指定します
# スレッド名・ホストとUserAgentの組み合わせの指定では、先頭「!」による否定条件の利用も可能です
@auto_post_prohibit_multiple_submissions = (
);

# 古スレageの自動書き込み禁止機能 制限対象設定
# 「無効:スレッド名:直前レスが何時間前:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:時間指定:メモ欄」のように指定します
# スレッド名・ホストとUserAgentの組み合わせの指定では、先頭「!」による否定条件の利用も可能です
@auto_post_prohibit_old_thread_age = (
);

# 以下の行は削除しないで下さい
1;
