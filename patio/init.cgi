#! /usr/bin/perl

#┌─────────────────────────────────
#│ Web Patio v3.4
#│ init.cgi - 2011/07/06
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────
$ver = 'きりしま式 Web Patio v3.4 k1.10';
# 2014/08/10 スレッドの連続作成、レスの連続投稿の処理ルーチンの変更
# 2013/11/17 本文の色づけと自動リンクの不具合の修正
# 2013/03/03 過去ログのバグ修正
# 2012/09/08 過去ログに落とす処理を修正
# 2011/07/06 3.4に合わせた
# 2011/04/27 3.31に合わせた
# 2010/11/14 スレッド番号の表示をオプションで選べるように
# 2010/06/23 新規スレッド作成とレスのタイマーを分けてみました
# 2009/07/31 禁止ワードにヒットした内容をログに残すようにしてみました
# 2009/06/15 レス数がおかしくなるバグの修正
# 2009/06/03 タイトル入力時に本文を直せなくするオプション検討中
# 2009/06/01 ユーザー間メール機能を無効にできるように
# 2009/04/10 Google AdSenseのコードをオプションで無効化できるように（よく忘れるので）
# 2009/04/07 新規作成時に表示をカスタムできるように
# 2009/03/18 FAQモードに挑戦
# 2009/03/14 スレッド作成制限モードの追加
# 2008/12/22 3.22に合わせた
# 2008/08/29 いったん一式アーカイブを更新
# 2008/01/15 レスお知らせメールの設定を追加
# 2007/12/17 管理者による編集時に、パスワードを消すかどうかオプションで指定できるようにした。
# 2007/11/14 過去ログ化<->復元（admin.cgiのみ変更）
# 2007/10/27 レスの全部表示
# 2007/06/10 3.2に合わせた
# 2007/06/10 3.14に合わせた
# 2007/05/01 3.13に合わせた
# 2007/03/05 3.0系に着手
# ベースバージョン
# $ver = 'WebPatio v3.4';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#│ 3. 添付画像のうち、以下のファイルを再配布しています。
#│  ・牛飼いとアイコンの部屋 (http://www.ushikai.com/)
#│    alarm.gif book.gif fold4.gif glass.gif memo1.gif memo2.gif
#│    pen.gif trash.gif mente.gif
#└─────────────────────────────────
#
# 【ファイル構成例】
#
#  public_html (ホームディレクトリ)
#      |
#      +-- patio /
#            |    patio.cgi     [705]
#            |    read.cgi      [705]
#            |    regist.cgi    [705]
#            |    admin.cgi     [705]
#            |    registkey.cgi [705]
#            |    init.cgi      [604]
#            |    note.html
#            |    mail.log      [606] *きりしま式で新設
#            |    search.log    [606] *きりしま式で新設
#            |    setting.cgi   [705] *きりしま式で新設
#            |
#            +-- data / index1.log  [606]
#            |          index2.log  [606]
#            |          memdata.cgi [606]
#            |
#            +-- lib / jcode.pl     [604]
#            |         upload.pl    [604]
#            |         edit_log.pl  [604]
#            |         find.pl      [604]
#            |         check.pl     [604]
#            |         registkey.pl [604]
#            |
#            +-- log  [707] /
#            |
#            +-- ses  [707] /
#            |
#            +-- upl [707] /
#            |
#            +-- img / *.gif
#                      faq.gif            *きりしま式で新設
#                      filenew.gif        *きりしま式で新設
#                      fold6.gif          *きりしま式で差替
#                      foldnew.gif        *きりしま式で新設
#                      mail.gif           *きりしま式で新設

#マイナスキーワードを設定する
@keyword = ('キーワード1 キーワード2');

#前日の設定
$d = 30;

use Time::Local;
use File::Basename qw/basename dirname/;
use File::Spec;
use Encode qw//;
use Symbol qw//;

#===========================================================
#  ◎基本設定
#===========================================================

# 外部ファイル
$jcode   = './lib/jcode.pl';
$upload  = './lib/upload.pl';
$editlog = './lib/edit_log.pl';
$findpl  = './lib/find.pl';
$checkpl = './lib/check.pl';
$regkeypl = './lib/registkey.pl';

# 書き込み禁止モード (0=通常動作 1=書き込み禁止)
$ReadOnly =0;

# 書き込み禁止モード中に表示するお知らせ
$Oshirase = 'メンテナンス中につき、書き込み禁止モードで動作しています。';

# 管理パスワード（英数字で8文字以内）
$pass = 'pass';

# スレッドログの閲覧、保存 Cookie ID
@thread_Edit = ( '01_hoge', '01_hoge2');

#全レス表示/途中レス番の表示
$middle_number = 50;
# アクセス制限をする
# 0=no 1=yes
$authkey = 0;

# ログイン有効期間（分）
$authtime = 60;

# 画像アップを許可する（親記事のみ）
# 0=no 1=yes
$image_upl = 1;

# トリップ機能（ハンドル偽造防止）のための変換キー
# →　英数字で2文字
$trip_key = 'ab';

# タイトル
$title = 'きりしま式 Web Patio 準備中';

# 掲示板の説明
$desc = 'ご自由に書き込み下さい';

# タイトルの文字色
$t_color = "#000000";

# タイトルサイズ
$t_size = '18px';

# 本文文字サイズ
$b_size = '13px';

# 本文文字フォント
$b_face = '"MS UI Gothic", Osaka, "ＭＳ Ｐゴシック"';

# メール本文用閲覧CGIのURL（read.cgiまでのフルパス）
$fullscript = 'http://freeden.e7.valueserver.jp/webpatio/patio/read.cgi';

# 掲示板本体CGI【URLパス】
$bbscgi = './patio.cgi';

# 掲示板投稿CGI【URLパス】
$registcgi = './regist.cgi';

# 掲示板閲覧CGI【URLパス】
$readcgi = './read.cgi';

# スレッド表示Ajax通信用API CGI【URLパス】
$readapicgi = './read_api.cgi';

# 掲示板管理CGI【URLパス】
$admincgi = './admin.cgi';

# 留意事項ページ【URLパス】
$notepage = './note.html';

# 現行ログindex【サーバパス】
$nowfile = './data/index1.log';

# 過去ログindex【サーバパス】
$pastfile = './data/index2.log';

# 会員ファイル【サーバパス】
$memfile = './data/memdata.cgi';

# 記録ファイルディレクトリ【サーバパス】
$logdir = './log';

# セッションディレクトリ【サーバパス】
$sesdir = './ses';

# 戻り先【URLパス】
$home = './patio.cgi';

# 壁紙
$bg = "";

# 背景色
$bc = "#F0F0F0";

# 文字色
$tx = "#000000";

# リンク色
$lk = "#0000FF";
$vl = "#800080";
$al = "#DD0000";

# 画像ディレクトリ【URLパス】
$imgurl = './img';

# 記事の更新は method=POST 限定 (0=no 1=yes)
# （セキュリティ対策）
$postonly = 1;

# 連続投稿の禁止時間（秒）※使用していません。下の2つで指定して下さい。
# $wait = 60;

# スレッド作成間隔（秒）（きりしま式で新設）
$wait_thread = 0;

# レス投稿間隔（秒）
$wait_response_default = 0;
$wait_response1 = 0;
$wait_response2 = 0;
$wait_response3 = 0;

# スレッドタイトルによる投稿間隔の変更(レス)
# (下記のいずれにも合致しない場合は、$wait_response_default および $responselog_default を使用します)
$wait_response_word1 = ''; # スレッドタイトル該当時、$wait_response1 および $responselog1 を使用します
$wait_response_word2 = ''; # スレッドタイトル該当時、$wait_response2 および $responselog2 を使用します
$wait_response_word3 = ''; # スレッドタイトル該当時、$wait_response3 および $responselog3 を使用します

# 新規投稿の記録ファイル（きりしま式で新設）
$threadlog = './thread.log';

# 返信の記録ファイル
$responselog_default = './response_default.log';
$responselog1 = './response1.log';
$responselog2 = './response2.log';
$responselog3 = './response3.log';

# $threadlog と $responselog に記録するホスト数（きりしま式で新設）
# 書き込み禁止時間が過ぎるとデータは破棄されるので、あまり大きな数を設定してもそこまで記録されないはず
$hostnum = 10;

# 日付別スレッド作成数ログファイル
$thread_create_countlog = './thread_create_count.log';

# 日付別レス書き込み数ログファイル
$response_countlog = './response_count.log';

# スレッド検索用最終更新日時記録SQLiteファイル
$thread_updatelog_sqlite = './db/thread_updatelog.sqlite';

# 検索期間指定の初期値指定
$d = 30;

# 禁止ワード
# → 投稿時禁止するワードをコンマで区切る　以下はきりしま式のサンプル掲示板で設定した禁止ワードの一覧
#　　必要に応じて行頭の # を削除して有効にしてください。
#    ２つ目以降のリストは「,」で区切ってから始めること。
#   （１つ目のリスト）$no_wd = 'アダルト,出会い,カップル';
#   （２つ目以降のリスト）$no_wd = $no_wd.',アダルト,出会い,カップル';
#    迷惑書き込みに多い「http」を指定するとかなり効果があると思われます
#    ピリオド「.」を使うと誤判定の元なので注意
# $no_wd = '';

# 禁止語の記録ファイル（きりしま式で新設）
$badwordlog = './badword.log';

#TODO 2017/10/26
#名前文字数制限用（トリップ含まない
$name_length_no_trip = 10;
#名前文字数制限用（トリップ含む
$name_length_trip = 5;
#スレッドタイトル文字数制限用
$sub_length = 10;
#TODO 2017/10/27

# スレッドタイトルが設定値に中間一致で合致するスレッドは、RSS（patio.cgi?mode=feedの一覧）に出力しません。
@rss_no_word=('テスト','kate2','アンカー','スマホ');

#　　ブロックログより抽出した効果のあったキーワード
$no_wd = '激安,スーパーコピー';

# フリーWeb系禁止ワード ※ユーザーの悪意のないページがはじかれる可能性があります
#                         メジャー系でないフリーWebの場合は、URL系禁止ワードに含まれているかもしれません
# $no_wd = $no_wd.',tripod,usearea';

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
# 半角独立濁点・半濁点(゛および゜): \N{U+FF9E}\N{U+FF9F}
# 全角独立濁点・半濁点(゛および゜): \N{U+309B}\N{U+309C}
# 半角スペース( ): \N{U+0020}
# 全角スペース(　): \N{U+3000}
# 半角感嘆符(!): \N{U+0021}
# 全角感嘆符(！): \N{U+FF01}
# 半角句読点(、および。): \N{U+FF64}\N{U+FF61}
# 全角句読点(、および。): \N{U+3001}\N{U+3002}
# 半角中点(・): \N{U+FF65}
# 全角中点(・): \N{U+30FB}
# 半角長音(ー): \N{U+FF70}
# 全角長音(ー): \N{U+30FC}
# ハイフンマイナス(-): \\\N{U+002D}
# 半角プラス(+): \N{U+002B}
# 全角プラス(＋): \N{U+FF0B}
# 半角ピリオド(.): \N{U+002E}
# 全角ピリオド(．): \N{U+FF0E}
# 半角等号(=): \N{U+003D}
# 全角等号(＝): \N{U+FF1D}
# 半角(#): \N{U+0023}
# 全角(#): \N{U+FF03}
# (◆): \N{U+25C6}
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
                      "\N{U+FF1D}", # 全角等号
                      "\N{U+0023}", # 半角(#)
                      "\N{U+FF03}", # 全角(#)
                      "\N{U+25C6}", # (◆)
                      );

# 日本語チェック（投稿時日本語が含まれていなければ拒否する）
# 0=No  1=Yes
$jp_wd = 1;

# URL個数チェック
# → 投稿コメント中に含まれるURL個数の最大値
$urlnum = 1;

# 名前入力必須 (0=no 1=yes)
$in_name = 0;

# E-Mail入力必須 (0=no 1=yes)
# E-Mail入力必須 (0=no 1=yes 2=入力欄非表示・入力禁止 3=入力禁止)
# ここを2や3にするとレスお知らせメール機能が利用できません。
$in_mail = 1;

# E-Mail表示 (0=非表示 1=表示) ※ここを表示にしても、ユーザーがメールアドレス非表示を選ぶと表示されません
# スパム防止のため、変更しないことを推奨。
$show_mail = 0;

# URL欄の入力判定
# 迷惑書き込み防止用 (0=なにもしない 1=必須 2=入力欄非表示・入力禁止 3=入力禁止)
# 2や3の場合は記事中にも表示されません。
$in_url = 2;

# 削除キー入力必須 (0=no 1=yes)
$in_pwd = 0;

# 1つのスレッドログフォルダ中のスレッドログファイル保存数
# スレッドログファイルを複数のフォルダに分割保存する際の
# 1つのフォルダ内に保存するスレッドログファイル数を設定します
# 0以下の数を設定する場合、$logdir直下に全てのスレッドログを保存します
# (設定変更した際は、管理画面から保存フォルダ再配置処理を行って下さい)
$number_in_threadlog_folder = 50000;

# 現行ログ最大スレッド数
# → これを超えると過去ログへ移動
$i_max = 1000;

# 過去ログ最大スレッド数
# → これを超えると自動削除
$p_max = 3000;

# 1スレッド当りの「表示」記事数
$t_max = 100;

# 1スレッド当りの「最大」記事数
# → これを超えると過去ログへ廻ります
# → 残り90%でアラームを表示します
$m_max = 1000;

# 現行ログ初期メニューのスレッド表示数
$menu1 = 20;

# 過去ログ初期メニューのスレッド表示数
$menu2 = 20;

# 色指定（順に、濃色、薄色、中間色）
$col1 = "#8080C0";
$col2 = "#FFFFFF";
$col3 = "#DCDCED";

# 繰越ページ数の当該ページの色
$pglog_col = "#DD0000";

# コメント入力文字数（全角換算）
$max_msg = 5000;

# JPG, PNG画像1枚あたりの最大投稿サイズ (bytes)
# → 例 : 102400 = 100KB
# 2MB=2048000
$maxdata = 5350000;

# GIF画像1枚あたりの最大投稿サイズ (bytes)
$maxdata_gif = 15350000;

# スマイルアイコンの使用 (0=no 1=yes)
$smile = 1;

# スマイルアイコンの定義 (スペースで区切る)
# → ただし、この設定箇所は変更しないほうが無難
# → 顔文字に半角カナや2バイト文字は使用厳禁（正規表現上の制約）
$smile1 = 'smile01.gif smile02.gif smile03.gif smile04.gif smile05.gif smile06.gif smile07.gif';
$smile2 = '(^^) (^_^) (+_+) (^o^) (^^;) (^_-) (;_;)';

# メール送信
# 0 : しない
# 1 : スレッド生成時
# 2 : 投稿記事すべて
$mailing = 0;

# メール送信先
$mailto = '';

# メール送信時の差出人
# 空欄 : メールアドレスの入力があればそのアドレス
# メールアドレスを指定 : つねに指定したメールアドレスから送信
$sender = '';

# メール送信先（ＢＣＣ）
$bccto = '';

# sendmailパス
# 通常はこれ
$sendmail = '/usr/sbin/sendmail';
# さくらインターネットはこっち
# $sendmail = '/usr/sbin/sendmail';

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$gethostbyaddr = 1;

# アクセス制限（半角スペースで区切る、アスタリスク可）
#  → 拒否ホスト名を記述（後方一致）【例】*.anonymizer.com
$deny_host = '';

#  → 拒否IPアドレスを記述（前方一致）【例】210.12.345.*
$deny_addr = '';

# VPNGate経由での書き込みを拒否
# 0 : 拒否しない
# 1 : 拒否する(書き込み時にエラーメッセージを表示します)
$deny_post_via_vpngate = 1;

# 画像分割保存 フォルダ番号ログファイル
# 画像ファイルを分割保存する際の
# フォルダ番号を記録するログファイルパスを設定します
$img_folder_number_log = './img_folder_number.log';

# 画像分割保存 フォルダ内画像数ログファイル
# 画像保存フォルダ内の画像ファイル数を記録する
# ログファイルパスを設定します
$imgfile_count_log = './imgfile_count.log';

# 画像分割保存 フォルダ内画像保存上限数
# 画像ファイルを分割保存する際に
# 1つのフォルダ内に保存する画像ファイルの上限数を設定します
$max_number_of_imgfiles_in_folder = 10000;

# 画像ディレクトリ（画像アップを許可するとき）
# → 順に、サーバパス、URLパス
$upldir = './upl';
$uplurl = './upl';

# 最大で画像6枚のアップロード
# アップロード可能枚数 増加数設定 (0～3枚)
$upl_increase_num = 3;

# アップ画像の表示時長辺最大サイズ（単位：ピクセル）
# → サムネイル画像機能有効時は、このサイズでサムネイル画像を表示します
$img_max_w = 200;	# 横幅
$img_max_h = 200;	# 縦幅

# アップ画像無変換ファイルサイズ上限(単位:バイト)
# アップ画像を"変換しない"ファイルサイズ上限値を設定します
# → この設定値よりも大きいファイルサイズのjpg/pngファイルがアップロードされた際に
#   アップ画像の変換が行われます
$img_no_convert_filesize_max = 0;

# アップ画像変換時JPEG圧縮品質設定
# アップ画像の変換を行う際のJPEG圧縮品質を設定します
# 1～100の間の整数で指定して下さい
$img_jpeg_compression_level = 80;

# アップ画像変換時最大横幅(単位:ピクセル)
# アップ画像の変換を行う際の最大横幅を設定します
# → 変換時にアップ画像横幅がこの設定値より大きい場合に
#   この設定値の横幅までアスペクト比を保って縮小されます
$img_convert_resize_w = 1600;

# アップ透過PNG画像変換時 アルファチャンネル合成色設定
# 透過PNGをJPEGに変換する際のアルファチャンネルとの合成色を設定します
# #rrggbb 形式で指定して下さい
$img_alphachannel_composite_color = '#ffffff';

# サムネイル画像を作成する（要：Image::Magick）
# → 縮小画像を自動生成し、画像記事の表示速度を軽くする機能
# 0=no 1=yes
$thumbnail = 1;

# サムネイル画像の生成時長辺最大サイズ（単位：ピクセル）
$thumb_max_w = 200;	# 横幅
$thumb_max_h = 200;	# 縦幅

# サムネイル画像JPEG圧縮品質設定
# サムネイル画像生成時のJPEG圧縮品質を設定します
# 1～100の間の整数で指定して下さい
$thumb_jpeg_compression_level = 80;

# サムネイル画像 アニメーションGIF 合成画像パス
# アニメーションGIFのサムネイル画像に合成する画像パスを設定します
$thumb_composite_img_path = './lib/play.gif';

# サムネイル画像 アニメーションGIF 合成画像 不透明度
# アニメーションGIFのサムネイル画像に合成する画像の不透明度を設定します
# 0～100の整数で指定して下さい
$thumb_composite_img_opacity = 70;

# サムネイル画像保存先ディレクトリ(ディレクトリのパーミッションは777である必要があります)
# → 順に、サーバパス、URLパス
$thumbdir = './thumb';
$thumburl = './thumb';

#画像のテキストリンクをPhotoSwipe対応に リンク修正
$domain_pc_name = 'http://hogehoge.com/patio/';

# アップ画像ファイル名表示の先頭に追加する文字列
# (本文検索時にも使用　大・小文字を区別します)
$img_filename_prefix = 'upl/';

## --- <以下は「投稿キー」機能（スパム対策）を使用する場合の設定です> --- ##
#
# 新規スレッド作成フォームでの投稿キーの使用
# → 0=no 1=yes
$regist_key_new = 0;

# スレッド内返信フォーム/ユーザー間メール送信フォームでの投稿キーの使用
# → 0=no 1=yes
$regist_key_res = 0;

# 投稿キー画像生成ファイル【URLパス】
$registkeycgi = './registkey.cgi';

# 投稿キー暗号用パスワード（英数字で８文字）
$pcp_passwd = 'patio123';

# 投稿キー許容時間（分単位）
#   投稿フォームを表示させてから、実際に送信ボタンが押される
#   までの可能時間を分単位で指定
$pcp_time = 30;

# 投稿キー画像の大きさ（10ポ or 12ポ）
# 10pt → 10
# 12pt → 12
$regkey_pt = 10;

# 投稿キー画像の文字色
# → $textと合わせると違和感がない。目立たせる場合は #dd0000 など。
$moji_col = '#dd0000';

# 投稿キー画像の背景色
# → $bcと合わせると違和感がない
$back_col = '#F0F0F0';

#-------------------------------------------------
#  ◎これ以下は きりしま式 の設定項目です。
#-------------------------------------------------

# 新着表示時間
# 単位：秒
# $hot = 43200; # 12時間
# $hot = 72000; # 20時間
$hot = 259200; # 72時間

# NEWの表示内容（HTML可）
$newmark = " <font color=#FF0000><b>NEW</b></font>";
# $newicon = ""; ブランクにすれば無効と同じ

# 新着のあるスレッドのアイコン
#$newfold = "foldnew.gif";

# 新着レスのアイコン
#$newfile = "filenew.gif";

# 色指定・注意色
$col4 = "#FF0000";

# 注意色の背景色
$col5 = "#FF9999";

# 投稿画面のコメント欄の行数
$rows = 15;

# 投稿画面のコメント欄の桁数
$cols = 72;

# 新規スレッド作成時のコメント欄の行数
$newrows = 20;

# レスのデフォルトタイトルの設定／題名後指定（プレビュー）
$restitle = 1;
# 0 : 空欄
# 1 : 「Re: 元のタイトル」＆プレビュー無効
# きりしま式はスレッド一覧にレスのタイトルが入るので 0 : 空欄 を強く推奨
# 1 にした場合は同時にプレビューも無効になります。

# スレッドの番号表示
$showthreadno = 1;
# 0 : 表示しない
# 1 : [スレッド番号]を表示する

# リンクの際のターゲット
$target="_blank";
# 記事内のリンクをクリックするたびに新しいウインドウを開きたくない場合は
# $target="_top"; # などを適当に設定

# 引用部分の色 >
$quotecol="#6495ED";

# 引用部分の色(2) *
$quotecol2="#FF6600";

# 引用部分の色(3) #
$quotecol3="#AAAAAA";

# ID機能の利用
# 0 : ID機能を利用しない
# 1 : ID機能を利用する
$idkey = 1;

# タイトルの文字数
$sublength = 80;

# メールの送信IP記録ファイル
$mailfile = './mail.log';

# メール送信可能間隔（秒）
$mailwait = 60;

# レスがあったときにお知らせ 0=しない 1=スレ立てた人のみ 2=コメントした人も含め全員
$mailnotify = 0;

# お知らせの送信元として使用するアドレス
$notifyaddr = '';

# お知らせの配信を拒否しているアドレス（,で区切って複数指定）
# この文字列にマッチした場合は配信されません（文字列なので注意））
$refuseaddr = '';

# 検索語の記録ファイル
$srchlog = './search.csv';

# 管理人が記事を編集した場合、書き込みをした本人が編集できないようにパスワードをクリアする
# 0 : パスワードを維持する
# 1 : パスワードをクリアする（本人編集不可）
$clearpass = 1;

# スレッド作成には、管理パスワードの入力を必須にする
# 有効にすると、実質的に管理者しかスレッドを立てることができなくなります。
# 0 : 無効にする
# 1 : 管理パスワードの入力を必須にする
$createonlyadmin = 0;

# スレッド作成時の注意書き（コメント欄の前に表示されます）
$createnotice = "";

# スレッド作成時のテンプレート（コメント欄に初期表示されます）
$createtemplate ="テンプレート展開\n\\nを使用することで\n複数行も対応";

# Google AdSenseのコードを表示させるルーチンを有効にするか設定します。
# コードは init.cgi の末尾の sub googleadsense 内に記述します。
# 0 : 無効にする
# 1 : 有効にする
$adsenseenable = 0;

# ユーザー間のメール送信機能
# メールアドレスを入力したユーザーがメールアドレスを非表示でメールを受け取る機能
# プロバイダーによってはセキュリティ上動作しない場合は無効にしてください。
# 0 : 無効にする
# 1 : 有効にする
$usermail = 1;

# プレビュー時に既入力文を編集できるか
# ('disabled'=戻って編集 ''=そのまま編集可能)
# 0=可 1=不可
$editpreview ='1';

# 禁止語の記録ファイル
$badwordlog = './badword.log';

#-------------------------------------------------
#  ◎取得するUserAgentの変更機能 設定項目
#-------------------------------------------------

# UserAgentから「,」と「:」を取り除き、「_」を「-」に置き換え、
# その後、この設定値で指定された文字列を取り除きます
# 設定値は「,」区切りで指定します
@useragent_remove_strings = (
);

#-------------------------------------------------
#  ◎NGレス(NGID/NGネーム)機能 設定項目
#-------------------------------------------------

# NGID/NGネームとして登録されたユーザーのコメントを置き換えるメッセージ
# (メッセージにHTMLを使用することができます)
$ngres_comment = "";

# NGID機能の利用
# ID機能が有効になっているとき($idkey = 1;)のみ利用できます
# 0 : NGID機能を利用しない
# 1 : NGID機能を利用する
$ngid = 1;

# NGIDの登録上限に達した後、さらに登録しようとした時のエラーメッセージ
$ngid_error_message = "NGID登録数の上限に達しています。";

# NGネーム機能の利用
# 0 : NGネーム機能を利用しない
# 1 : NGネーム機能を利用する
$ngname = 1;

# NGネームの登録上限に達した後、さらに登録しようとした時のエラーメッセージ
$ngname_error_message = "NGネーム登録数の上限に達しています。";

# NGネーム適用レス名前欄カット表示機能 最低表示文字数
# この文字数を超える名前欄の文字について、NGネーム適用レスの時に表示が隠されます
# -1など0未満の値を設定すると、NGネーム適用レスでも名前欄を全て表示します
$ngname_dispchar_length = 3;

# NGレス時 被参照レス件数 非表示機能
# 被参照レス件数表示「n件のレス」が表示されているレスがNGレスの時に、
# 被参照レス件数表示を非表示にします
# (非表示にするかどうかの設定で、通常と指定が逆になりますのでご注意下さい)
# 0 : NGレス時にも被参照レス件数を表示します
# 1 : NGレス時には被参照レス件数を表示しません
$ngres_hide_refcounter = 1;

# 連鎖NG機能 デフォルト値設定
# 連鎖NG機能の有効/無効がユーザーによって設定されていない時の
# デフォルト値を設定します
# 0 : 連鎖NG機能を無効にする
# 1 : 連鎖NG機能を有効にする
$chain_ng = 1;

#-------------------------------------------------
# ◎被参照レス件数表示・展開表示機能 設定項目
#-------------------------------------------------

# 被参照レス件数カウント 非対象レス アンカー数設定
# 設定数以上のアンカーを含むレスは、カウント対象になりません
$number_of_anchor_made_ref_count_exempt = 6;

#-------------------------------------------------
#  ◎NGスレッド機能 設定項目
#-------------------------------------------------

# NGスレッド表示 デフォルト値設定
# NGスレッド表示設定がユーザーによって設定されていない時の
# デフォルト値を設定します
# 0 : スレッドを非表示にする
# 1 : スレッド名を置換する
$ngthread_default_display_mode = 0;

# スレッド作成者のNG設定 限定一致設定
# スレッド作成者名にこの設定値の文字列のいずれかが含まれる場合、
# スレッド一覧画面のスレッド作成者のNG設定でこの設定値と同じ文字列を含み、
# 同行全体の設定にも一致した場合にNGスレッドとして判定します
@ngthread_thread_creator_must_include_strings = (
);

# レス投稿時スレッド作成者名上書き 対象レス範囲設定
# レス投稿時に、レスNo.が >>2からこの設定値までとなる場合に
# >>1とホストまたは登録ID、またはCookieA、または書込IDが同じ場合に
# スレッド一覧画面でのスレッド作成者名を書き込み時の名前で上書きします
$ngthread_thread_list_creator_name_override_max_res_no = 7;

# レス投稿時スレッド作成者名上書き 除外投稿者名設定
# レス投稿時にスレッド作成者名上書きの対象となっても、
# 書き込み時の名前に この設定値のいずれかの文字列を含む場合は、
# 上書きの対象から除外します
@ngthread_thread_list_creator_name_override_exclude_names = (
);

# レス投稿時スレッド作成者名上書き 判定除外ホスト設定
# レス投稿時にスレッド作成者名上書きの対象判定時に
# この設定値のいずれかの文字列を含むホストの場合は、同一ホスト判定を行いません
@ngthread_thread_list_creator_name_override_exclude_hosts = (
);

#-------------------------------------------------
#  ◎ユーザ強調表示機能
#  　UserAgentの強調表示機能 設定項目
#-------------------------------------------------

# 外部ログファイル(JSON)パス
$highlight_userinfo_log_path = './highlight_userinfo.json';

# ユーザ強調表示機能 記録情報 保持時間
$highlight_userinfo_hold_hour = "336";

# UserAgentの強調表示機能 記録情報 保持時間
$highlight_ua_hold_hour = "336";

#-------------------------------------------------
#  ◎管理画面 動作設定機能
#-------------------------------------------------

# 管理画面での動作設定機能の利用
# 0 : 動作設定機能を利用しない
# 1 : 動作設定機能を利用する
$conf_override = 1;

# 動作設定の記録ファイルパス
# 【init.cgiから見たパスを指定して下さい】
$conf_override_path = "./init-override.cgi";

#-------------------------------------------------
#  ◎WebProtect連携 登録ID認証機能
#-------------------------------------------------

# 新規スレッド作成フォームでのWebProtect登録ID認証機能の利用
# 0 : 登録ID認証機能を利用しない
# 1 : 登録ID認証機能を利用する
$webprotect_auth_new = 0;

# スレッド内返信フォームでのWebProtect登録ID認証機能の利用
# 0 : 登録ID認証機能を利用しない
# 1 : 登録ID認証機能を利用する
$webprotect_auth_res = 0;

# 認証時に登録IDが見つからなかった時のエラーメッセージ
$webprotect_auth_id_notfound_msg = "登録IDが見つからないか、登録パスワードが正しくありません。";

# 認証時に登録パスワードが正しくなかった時のエラーメッセージ
$webprotect_auth_pass_mismatch_msg = "登録IDが見つからないか、登録パスワードが正しくありません。";

# WebProtect ディレクトリパス
# 【このinit.cgiから見たパスを指定して下さい】
$webprotect_path = '../protect';

# 登録ID認証成功ログ機能の利用
# スレッド作成時・レス投稿時に認証に成功した登録IDを記録します
# 0 : 登録ID認証成功ログ機能を利用しない
# 1 : 登録ID認証成功ログ機能を利用する
$webprotect_authlog = 1;

# 登録ID認証成功ログ機能ログファイルパス
# 【このinit.cgiから見たパスを指定して下さい】
$webprotect_authlog_path = './kakikomi.log';

#-------------------------------------------------
#  ◎アップロードしない画像のMD5ハッシュ値設定
#-------------------------------------------------

# アップロードしない画像 MD5ハッシュ値設定
# アップロードしようとする画像のMD5がここで指定した値に合致する場合に無視し、
# アップロードしなかったものとして取り扱います
@ignore_img_md5hash = (
);

#-------------------------------------------------
#  ◎アップロード禁止画像指定機能
#-------------------------------------------------

# アップロード禁止チェック通過画像 MD5ハッシュ値ログファイルパス
# アップロードに成功したファイルのMD5ハッシュ値のログファイルパスを設定します
$img_md5hash_log_path = './img_md5hash.log';

# アップロード禁止画像ファイル MD5ハッシュ値設定
# 禁止画像として検知する、オリジナル画像ファイルのMD5ハッシュ値を設定します
# 入力例: 'd41d8cd98f00b204e9800998ecf8427e',
@prohibit_img_md5hash = (
);

#-------------------------------------------------
#  ◎同一画像アップロード禁止機能
#-------------------------------------------------

# 同一画像アップロード禁止機能の利用
# アップロード画像のMD5をチェックし、
# 同じ値のアップロード画像が複数ある場合にエラー画面を表示します
# 0 : 同一画像アップロード禁止機能を利用しない (チェックしない)
# 1 : 同一画像アップロード禁止機能を利用する
$prohibit_same_img_upload = 1;

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
#  ◎キーワード一致判定 設定項目
#-------------------------------------------------
# 変数 外部ファイルパス
$match_variable_settings_filepath = './match_variable_settings.csv';

# ひらがな・カタカナ 判定モード設定
# 設定値のひらがな・カタカナで、全角と半角を区別しないで一致判定を行う以外に
# 大文字と小文字を区別しないで一致判定を行うかどうかを設定します
# 0 : ひらがな・カタカナの全/半角のみ区別せずに判定します (大/小文字は区別されます)
# 1 : ひらがな・カタカナの全/半角と大/小文字を全て区別せずに判定します
$match_hiragana_katakana_normalize_mode = 1;

#-------------------------------------------------
#  ◎初回書き込みまでの時間制限機能
#-------------------------------------------------
# 外部ファイルパス
$firstpost_restrict_settings_filepath = './firstpost_restrict_settings.csv';

# 初回書き込みまでの時間制限機能 対象外ユーザー設定
# 制限対象から除外するユーザーを
# 「ホスト<>UserAgent:CookieA or 登録ID or 書込ID」のように指定します
@firstpost_restrict_exempt = (
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
#  ◎ホストなどによるユーザ間メールの連続送信制限機能
#-------------------------------------------------

# メール送信を拒否するユーザー
# 'ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:メモ欄' のリストで設定します
@usermail_prohibit = (
);

# mail.log($mailfile)に記録しないユーザー
# 'ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:メモ欄' のリストで設定します
@usermail_not_record = (
);

# 同じレスの送信を制限する時間 (単位:秒)
$usermail_time_of_continuously_send_restricting = 180;

# メール送信先アドレス
$usermail_to_address = 'hoge@example.com';

#-------------------------------------------------
#  ◎スレッド閲覧制限機能 設定項目
#-------------------------------------------------

# スレッド閲覧制限対象ユーザー
# '無効:スレッド名:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:CookieAの有無:日付による除外:CookieA or 登録ID or 書込IDの除外:メモ欄' のリストで設定します
# (先頭の「無効」のフィールドに ▼ がセットされている設定は、制限対象判定を行いません)
@thread_browsing_restrict_user = (
);

# スレッド閲覧制限対象時リダイレクト先URL
$thread_browsing_restrict_redirect_url = 'http://hogehoge.com/';

#-------------------------------------------------
#  ◎外部ファイルによる自動禁止機能などの統合
#-------------------------------------------------

# 外部ファイルパス
$prohibit_suppress_settings_filepath = './prohibit_suppress_settings.csv';

#-------------------------------------------------
#  ◎自動書き込み禁止機能
#-------------------------------------------------

# 自動書き込み禁止機能 消去ログファイル(CSV)パス
$auto_post_prohibit_log_path = './auto_prohibit.csv';

# 自動書き込み禁止機能 累積ログファイル(CSV)パス
$auto_post_prohibit_no_delete_log_path = './auto_prohibit_no_delete.csv';

# 自動書き込み禁止機能 消去ログ 消去時間 (単位:秒)
# 自動書き込み禁止機能判定時に消去時間を経過しているログを判定から除外し、
# ログ書き込み時に自動消去します
# また、0に設定すると自動消去しません
$auto_post_prohibit_delete_time = 300;

# 自動書き込み禁止機能 書き込み禁止対象時 リダイレクト先URL
# 相対パス指定時には、regist.cgiから見たURLに変換してリダイレクトします
# 未指定時にはリダイレクトを行いません
$auto_post_prohibit_redirect_url = './patio.cgi';

# 自動書き込み禁止機能 レス返信時 ログURL列出力 先頭文字列
@auto_post_prohibit_log_concat_url = ('http://hogehoge.com/read.cgi?no=');

# スレッドタイトル(否定条件)・変換前/変換後画像のMD5・一致時ログ出力コメント・ホスト名とUserAgent・CookieA or 登録ID or 書込IDの組み合わせ
@auto_post_prohibit_combination_imgmd5 = (
);

## 自動書き込み禁止機能 自動消去ログ存在時リダイレクトの判定要素追加 対象ホスト設定 ##
# 自動消去ログとホストが一致した場合に、
# さらに、CookieAが一致する必要があるホストを設定します
# ホストは中間一致で判定します
@auto_post_prohibit_additional_match_required_host = (
);

## 自動書き込み禁止機能 名前欄の除外機能 ##
#
# この設定値に合致する名前の投稿の場合は、
# 「自動書き込み禁止機能(名前)」の判定を行いません
$auto_post_prohibit_exempting_name = '';

## スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能 ##
#
# ログファイル(JSON)パス
$auto_post_prohibit_thread_number_res_target_log_path = './auto_prohibit_thread_number_res_target.json';

# [設定時間1]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_1 = "1";

# [設定時間2]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_2 = "2";

# [設定時間3]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_3 = "3";

# [設定時間4]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_4 = "4";

# [設定時間5]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_5 = "5";

# [設定時間6]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_number_res_target_hold_hour_6 = "6";

## スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能 ##
#
# ログファイル(JSON)パス
$auto_post_prohibit_thread_title_res_target_log_path = './auto_prohibit_thread_title_res_target.json';

# [設定時間1]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_1 = '1';

# [設定時間2]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_2 = '2';

# [設定時間3]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_3 = '3';

# [設定時間4]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_4 = '4';

# [設定時間5]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_5 = '5';

# [設定時間6]をクリックして追加した場合の設定保持時間
$auto_post_prohibit_thread_title_res_target_hold_hour_6 = '6';

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

# 指定したレスNoまでの自動書き込み禁止機能
# 「レス番号:スレッド名:レス1の除外単語:制限単語:文字数除外:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:時間指定:メモ欄」のように指定します
# スレッド名・ホストとUserAgentの組み合わせの指定では、先頭「!」による否定条件の利用も可能です
@auto_post_prohibit_up_to_res_number = (
);

## 複数回投稿時の自動書き込み禁止機能 ##

# 制限対象設定
# 「無効:スレッド名:レス1の除外単語:制限単語:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:時間指定:メモ欄」のように指定します
# スレッド名・ホストとUserAgentの組み合わせの指定では、先頭「!」による否定条件の利用も可能です
@auto_post_prohibit_multiple_submissions = (
);

# ユーザー投稿カウントログ ファイルパス
$auto_post_prohibit_multiple_submissions_count_log_path = './auto_post_prohibit_multiple_submissions.log';

# リダイレクトする同一ユーザー投稿数
# 同じユーザーがこの数以上の投稿を行っている場合、リダイレクト対象として判定します
$auto_post_prohibit_multiple_submissions_redirect_threshold = 4;

# ユーザー投稿カウントログ 消去時間 (単位:分)
# 複数回投稿時の自動書き込み禁止機能の判定時に
# 消去時間を経過しているログを判定から除外し、ログ書き込み時に自動消去します
$auto_post_prohibit_multiple_submissions_log_hold_minutes = 60;

## 古スレageの自動書き込み禁止機能 ##

# 制限対象設定
# 「無効:スレッド名:直前レスが何時間前:ホスト<>UserAgent:CookieA or 登録ID or 書込ID:プライベートモード:時間指定:メモ欄」のように指定します
# スレッド名・ホストとUserAgentの組み合わせの指定では、先頭「!」による否定条件の利用も可能です
@auto_post_prohibit_old_thread_age = (
);

# ユーザー古スレage投稿カウントログ ファイルパス
$auto_post_prohibit_old_thread_age_count_log_path = './auto_post_prohibit_old_thread_age.log';

# リダイレクトする同一ユーザー投稿数
# 同じユーザーがこの数以上の古スレage投稿を行っている場合、リダイレクト対象として判定します
$auto_post_prohibit_old_thread_age_redirect_threshold = 4;

# ユーザー古スレage投稿カウントログ 消去時間 (単位:分)
# 古スレageの自動書き込み禁止機能の判定時に
# 消去時間を経過しているログを判定から除外し、ログ書き込み時に自動消去します
$auto_post_prohibit_old_thread_age_log_hold_minutes = 60;

#-------------------------------------------------
#  ◎外部ファイルによるスレッド作成制限機能などの統合
#-------------------------------------------------

# 外部ファイルパス
$thread_create_post_restrict_settings_filepath = './thread_create_post_restrict_settings.csv';

#-------------------------------------------------
#  ◎スレッド画面からユーザを制限する機能
#-------------------------------------------------

# ログファイル(JSON)パス
$restrict_user_from_thread_page_target_log_path = './restrict_user_from_thread_page_target.json';

## 設定時間1 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_1 = '1';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_1 = '設定時間1 1h';

## 設定時間2 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_2 = '3';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_2 = '設定時間2 3h';

## 設定時間3 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_3 = '6';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_3 = '設定時間3 6h';

## 設定時間4 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_4 = '24';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_4 = '設定時間4 1day';

## 設定時間5 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_5 = '72';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_5 = '設定時間5 3day';

## 設定時間6 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_6 = '168';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_6 = '設定時間6 7day';

## 設定時間7 ##
# 設定保持時間
$restrict_user_from_thread_page_target_hold_hour_7 = '720';
# 追加リンク・プルダウンメニュー表示名
$restrict_user_from_thread_page_target_type_name_7 = '設定時間7 30day';

#-------------------------------------------------
#  ◎スレッド画面からユーザを時間制限する機能
#-------------------------------------------------

# ログファイル(JSON)パス
$restrict_user_from_thread_page_by_time_range_target_log_path = './restrict_user_from_thread_page_by_time_range_target.json';

# [設定時間1]をクリックして追加した場合の設定保持時間
$restrict_user_from_thread_page_by_time_range_target_hold_hour_1 = '72';

# [設定時間2]をクリックして追加した場合の設定保持時間
$restrict_user_from_thread_page_by_time_range_target_hold_hour_2 = '168';

# [設定時間3]をクリックして追加した場合の設定保持時間
$restrict_user_from_thread_page_by_time_range_target_hold_hour_3 = '336';

# [設定時間4]をクリックして追加した場合の設定保持時間
$restrict_user_from_thread_page_by_time_range_target_hold_hour_4 = '504';

# 制限時間範囲
# HHmm-HHmm(時を00～23 分を00～59)の書式で指定します。
# また、時間範囲の始めが終わりよりも後に指定されている場合、時間範囲終わりを翌日の時刻として取り扱います。
# 例: 「2300-0600」と指定した場合、当日23:00:00～翌日06:00:59までを判定対象時間とします。
$restrict_user_from_thread_page_by_time_range_enable_time_range = '0000-0600';

#-------------------------------------------------
#  ◎スレッド画面からユーザを制限する機能 (そのスレのみ)
#-------------------------------------------------

# ログファイル(JSON)パス
$in_thread_only_restrict_user_from_thread_page_target_log_path = './in_thread_only_restrict_user_from_thread_page_target.json';

# [設定時間]をクリックして追加した場合の設定保持時間
$in_thread_only_restrict_user_from_thread_page_target_hold_hour = '336';

#-------------------------------------------------
#  ◎スレッド作成・レス時のreCAPTCHA認証機能
#-------------------------------------------------

# reCAPTCHA Site Key 設定
$recaptcha_site_key = "6LdmHRATAAAAAKr58AhPfczV1py1w73eNk3jtHKw";

# reCAPTCHA Secret Key 設定
$recaptcha_secret_key = "6LdmHRATAAAAAOG8FHjpINMRdkaWx1lixmh9jCV7";

# スレッド作成時のreCAPTCHA認証機能の利用
# 0 : 利用しない
# 1 : 利用する
$recaptcha_thread = 0;

# スレッド作成時の消去ログ(スレッド作成カウントログ)パス
$recaptcha_thread_create_log = "./recaptcha_thread_create_log.csv";

# スレッド連続作成数カウント時間 (単位:秒)
# 本機能のスレッド作成カウントログで
# この時間を超えたログについて自動消去されます
# また、0に設定すると自動消去しません
$recaptcha_thread_count_time = 600;

# スレッド連続作成許容数
# スレッド連続作成数カウント時間内に
# この数を超えてスレッド作成を行おうとすると、reCAPTCHA認証の対象となります
#
# 例: 設定値に5を設定した場合、
#     連続作成数カウント時間内に5件のスレッド作成があった後に
#     スレッド作成フォームを表示する時にreCAPTCHAが表示されます
$recaptcha_thread_permit = 5;

# スレッド作成時の累積ログパス
# スレッド作成時の削除ログと同内容で自動消去を行わないログです
$recaptcha_thread_create_log_no_delete = "./recaptcha_thread_create_log_no_delete.csv";

# スレッド作成時のreCAPTCHA認証対象ホストログパス
$recaptcha_thread_auth_host_log = "./recaptcha_thread_auth_host_log.csv";

# スレッド作成時のreCAPTCHA認証対象ホストログ 消去時間 (単位:秒)
# reCAPTCHA認証対象ホストで書き込みで成功した場合に
# 消去時間を経過していた場合は、ログから消去します
# また、0に設定すると自動消去しません
$recaptcha_thread_auth_host_release_time = 300;

# レス時のreCAPTCHA認証機能の利用
# 0 : 利用しない
# 1 : 利用する
$recaptcha_res = 0;

#-------------------------------------------------
#  ◎検索時のreCAPTCHA認証機能
#-------------------------------------------------

# reCAPTCHA Site Key 設定
$find_recaptcha_site_key = $recaptcha_site_key;

# reCAPTCHA Secret Key 設定
$find_recaptcha_secret_key = $recaptcha_secret_key;

# 検索時のreCAPTCHA認証機能の利用
# 0 : 利用しない
# 1 : 利用する
$find_recaptcha = 0;

# 連続検索数カウント時間 (単位:秒)
# 本機能の検索数カウントログで
# この時間を超えたログについて自動消去されます
# また、0に設定すると自動消去しません
$find_recaptcha_count_time = 600;

# 連続検索許容数
# 連続検索数カウント時間内に
# この数を超えて検索を行おうとすると、reCAPTCHA認証の対象となります
#
# 例: 設定値に5を設定した場合、
#     連続検索数カウント時間内に5回の検索があった後に
#     検索フォームを表示する時にreCAPTCHAが表示されます
$find_recaptcha_permit = 5;

# 検索時のreCAPTCHA認証対象ホストログ 消去時間 (単位:秒)
# reCAPTCHA認証対象ホストで書き込みで成功した場合に
# 消去時間を経過していた場合は、ログから消去します
# また、0に設定すると自動消去しません
$find_recaptcha_auth_host_release_time = 300;

# 消去検索ログ(検索数カウントログ)パス
# 累積検索ログパスは、$srchlog で設定します
$find_recaptcha_count_log = "./recaptcha_find_log.csv";

# 検索時のreCAPTCHA認証対象ホストログパス
$find_recaptcha_auth_host_log = "./recaptcha_find_auth_host_log.csv";

# 同一条件検索時のreCAPTCHA認証スキップ機能の利用
# 0 : 利用しない
# 1 : 利用する
$find_recaptcha_continue = 0;

# 同一条件 連続検索数カウント時間 (単位:秒)
# 同一条件でのページ遷移による連続検索をカウントします
# この時間を超えた検索はカウントから除外・消去されます
$find_recaptcha_continue_count_time = 600;

# 同一条件 連続検索許容数
# $find_recaptcha_permitを超えた検索でも、
# 同一条件かつ本設定値以内であれば、reCAPTCHA認証をスキップします
$find_recaptcha_continue_permit = 3;

### 同一条件検索時のreCAPTCHA認証スキップ Cookie暗号化 ###
# 同一条件検索時にreCAPTCHA認証をスキップするため、
# セッションCookieに検索条件を暗号化保存して利用します
#
# *** 2048bit以上 *** の鍵長を持つRSA鍵を、opensslコマンドや、
# http://travistidwell.com/jsencrypt/demo/ などのWebサイト上で作成し、
# 秘密鍵・公開鍵をそれぞれ設定して下さい
#
# 鍵は複数行に渡りますので、クォーテーション間にそのまま貼り付けて下さい
#
# 秘密鍵 (-----BEGIN RSA PRIVATE KEY----- と -----END RSA PRIVATE KEY----- を含めてそのまま貼り付けて下さい)
$find_recaptcha_continue_cookie_rsa_private_key = '
-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQBDTneEMi3GdlcsWOMbr+8S+oT+GJcdgSsMOCfg2loSNCIaS1OF
qC8SCjgTVqPGF9kvl/Ohs4aSZPIjeGHl9w5Z22XSrGSnh0xCKkTT7mCQ0qrNivkC
EpDSF0KHU2YTvKzML45fW4x6ssuPx1D1334GNEmuyKTdqvkkcJtro46K+hg+3YFO
5G5KobSnGbcRmtNO/UOoMaW7NJgAwEYssObOsZL5uWGsTKn1HR5gndzAkctr8Fo/
+/zQ6pTolm34AnbK5D2vQDGzQFxQvAxJs17khzCk2e2gdbmmVAtsqBlVI2EqXIkY
L6G3lo7CVvSZH52OD684JLAvlR9HdO034nWNAgMBAAECggEAMAhlfrAYvtNhbsKY
gP/TS+YA1x1Rarrtr7C7tNnfAbK2y7EKEA5wWR1120cvZYVLd42nTrTByuPDcdDN
fMINOc87IVfqFSyXHXjw2ZX60B+nyTvubK43L9dtoQnBhUBWyPj/T8oTvNSwNRF3
E6DFXUQfeV6zWYZUes7p+60jYsZQ8z0jIKgRdWCx/v88DRJiBLONLK7WWJOg+3o+
z5n9teg524rMm+NQ+7s7ZPY4q4G69LlQvq9Qb3rM41FuuaYJSN0swBeI2aU3nGQB
zr4Ab9XrvZv/2fA/Ljy1v//SsqUoPPkyvO9km0tvD3nyiWAb9ZPyV6PDz7mCPrvO
+6+GuQKBgQCGXKpW0gp5nx+Lwlo+OQqCWihqfy9skNHdYLw2ZHcMgqIkQ/JylhoH
TwYmFfs9oxFHeWP+IPT0SNky6agW7S3XHgUdarn0jW7IEVrtZiqas5fA7udcBgG+
zgN+WqjDDBGkgFE6kiOyImjDCN+LojLxEYOW2/jJIA9WAu7Q1XZ5SwKBgQCAPTmq
pcbA9V5HPad98hcXkLX3iZAVEKCHPm0IXFvkLApEROLWZaRWyjx1NXcpyOZjLhar
ZpbDhuwxdJFX6YOcA5TtmN7zIJizmjtweV6UlS0/G5f2OvAz0ovMHHy2HVM6qmiU
DzbUV6T/bxuNVbZx7oTZOtkApaJY+yUCyCEdhwKBgCXwOmTDcBPBW33yBds17gK6
hFj1yqVECw4QR3SwT3En3bKRwP6b5YOUy66rXEKeLb3Zx+M02RW1ECcxFLZMiDoK
jvUsco9b9CDnzZ3k0DjYZwwiKQ+x3oJK12+xF5/jY4Poe4cnRo8A6kXP1pct2GZ7
RIWvXQMlW081CsvKymYbAoGAaShLmmi4U9ChT8/6Aeg8EWHkJalTUkLBMEX7iMib
vb5zaMoILQFKQrUx4HdIUSZh7eCETGciqBGCq4dIDAv7lTrGrBMYd8w6C8UkirWr
3jF52e8ZrJtmD0jOxEBz766aalgEy6yyLGv2bFPDByHLKyAJJk0AV2x7dXX0QpSz
uw8CgYAuFwME4Bzg9Fd4+N0WC9mFbg4631VjaG35oFTOCMJqYKbkmPANWKWUl+Ak
cPtpEeXSsqUxyO2UmTD7XYTOLj+IvKp9KXWtMIOhqIvSXpJ0pKgOJ3Z5mvhhlTme
m50WX8g+3i5mxKgbaH8qA01Bu8Q6vFRMpLSyNHMGDGi57Q0s2Q==
-----END RSA PRIVATE KEY-----
';
#
# 公開鍵 (秘密鍵と同様に、開始行・終了行を含めてそのまま貼り付けて下さい)
# -----BEGIN PUBLIC KEY----- と -----END PUBLIC KEY----- の形式、もしくは、
# -----BEGIN RSA PUBLIC KEY----- と -----END RSA PUBLIC KEY----- の形式が利用可能です
$find_recaptcha_continue_cookie_rsa_public_key = '
-----BEGIN PUBLIC KEY-----
MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQBDTneEMi3GdlcsWOMbr+8S
+oT+GJcdgSsMOCfg2loSNCIaS1OFqC8SCjgTVqPGF9kvl/Ohs4aSZPIjeGHl9w5Z
22XSrGSnh0xCKkTT7mCQ0qrNivkCEpDSF0KHU2YTvKzML45fW4x6ssuPx1D1334G
NEmuyKTdqvkkcJtro46K+hg+3YFO5G5KobSnGbcRmtNO/UOoMaW7NJgAwEYssObO
sZL5uWGsTKn1HR5gndzAkctr8Fo/+/zQ6pTolm34AnbK5D2vQDGzQFxQvAxJs17k
hzCk2e2gdbmmVAtsqBlVI2EqXIkYL6G3lo7CVvSZH52OD684JLAvlR9HdO034nWN
AgMBAAE=
-----END PUBLIC KEY-----
';

#-------------------------------------------------
#  ◎表示内容分岐機能
#-------------------------------------------------
# スレッドページで表示範囲のレスに
# 設定した文字列を含むか、画像アップチェックが有効の場合は画像が含まれている場合に、
# 表示内容を変更して出力します

# 表示内容分岐機能 対象文字列設定
@contents_branching_keyword = ('テンプレート');

# 表示内容分岐機能 画像アップチェック
# 0 : チェックしない
# 1 : チェックする
$contents_branching_img_check = 1;

#-------------------------------------------------
#  ◎書き込みログ出力機能
#-------------------------------------------------
# スレッド作成/レス返信による書き込みログを出力します

# 書き込みログ出力機能の利用
# 0 : 利用しない
# 1 : 利用する
$post_log = 1;

# 書き込みログ 出力ディレクトリパス
# このディレクトリは予め作成し、パーミッションを書き込み可能に設定して下さい
$post_log_dir = './kakikomi';

# 書き込みログファイル名 末尾文字列
# 書き込みログファイル名の先頭に付与する日付(YYYYMMDD)に続くファイル名を指定して下さい
$post_log_filename_suffix = 'log.csv';

# 書き込みログ 固定出力文字列
$bbs_pass = 'bbs1';

# 書き込みログ カテゴリ名変換設定
# スレッド名末尾に含まれるカテゴリキーワードと
# 書き込みログに出力するカテゴリ名の対応を設定して下さい
#
# 設定例: @category_convert = ('test:テスト');
#   動作: スレッドタイトル末尾に「test」を含む場合、
#         書き込みログ「カテゴリ」欄に「テスト」と出力し、
#         「スレッド名」欄に、スレッドタイトル末尾から「test」を除いて出力します
@category_convert = (
);

# 書き込みログの置換記録機能
# 書き込みログのレス内容列に記録する内容が設定値に部分一致する場合、
# 一致した変換前文字列に対応する変換後文字列を「;」で区切り、書き込みログに記録します
#
# 設定値は「'変換前:変換後'」の書式で指定します
# 複数指定する場合は、「,」で区切り、設定例のように指定します
#
# 設定例: @post_log_contents_replace = ('変換前1:変換後1', '変換前2:変換後2');
@post_log_contents_replace = (
);

#-------------------------------------------------
#  ◎書き込み履歴関連設定
#-------------------------------------------------
# 書込ID管理WebProtectと共有する設定値のハッシュ宣言 (この項目は設定不要です)
%history_shared_conf;

# 書込ID管理WebProtectフォルダパス
$history_webprotect_dir = './protect_rireki';

# 書込ID管理WebProtect 書込ID発行ページURL
# スレッド表示画面(read.cgi)の
# 「書込IDが未発行なので記録されません。【書込IDを発行する】」リンクの移動先URL
$history_webprotect_issue_url = "$history_webprotect_dir/index.cgi";

# 書込ID管理WebProtectのinit.cgiで
# 書込ID発行形態をユーザ操作 ($cf{pwd_regist} = 1;) にした場合の
# 書込ID発行完了画面の戻り先【URLパス】
# ※ 相対パスにて指定する場合は、このファイルから見たパスを指定して下さい
$history_shared_conf{back_url} = "$history_webprotect_dir/index.cgi";

# 書込ID発行間隔（秒）
$history_shared_conf{wait_regist} = 60;

# 書込ID発行間隔制限 除外ホスト
@{$history_shared_conf{wait_regist_exempt_hosts}} = (
);

# 書き込み履歴ページ表示CGIパス
$historycgi = './history.cgi';

# 書き込み履歴ログ保存フォルダ
$history_shared_conf{history_logdir} = './history';

# 1つの書き込み履歴ログフォルダ中の書き込み履歴ログファイル保存数
# 書き込み履歴ログファイルを複数のフォルダに分割保存する際の
# 1つのフォルダ内に保存する書き込み履歴ログファイル数を設定します
$history_shared_conf{number_of_logfile_in_history_logdir} = 10000;

# 書き込み履歴ログファイル分割保存 フォルダ番号ログファイル
# 書き込み履歴ログファイルを分割保存する際の
# フォルダ番号を記録するログファイルパスを設定します
# ※ 相対パスにて指定する場合は、このファイルから見たパスを指定して下さい
$history_shared_conf{history_logdir_number} = './history_logdir_number.log';

# 書き込み履歴ログファイル分割保存 フォルダ内ログファイル数カウンタファイル
# 保存フォルダ内の書き込み履歴ログファイル数を記録するログファイルパスを設定します
# ※ 相対パスにて指定する場合は、このファイルから見たパスを指定して下さい
$history_shared_conf{history_logfile_count} = './history_logfile_count.log';

# 書き込み履歴ログ 履歴記録上限数
$history_save_max = 100;

# 書き込み履歴ログ 記録除外スレッドタイトル
# 通常文字列の部分一致判定を行い、スレッドタイトルとこの設定値のいずれかが合致した場合、
# 書き込み履歴ログへの記録を行いません
@history_save_exempt_titles = (
);

# 書き込み履歴ページ 1ページあたりのスレッド表示数
$history_display_menu = 50;

#-------------------------------------------------
#  ◎ここまで読んだ機能
#-------------------------------------------------

# 履歴追加完了メッセージの「履歴」リンク先URL
$readup_to_here_added_history_link_url = $historycgi;

# 書込IDを保持していないときのエラーメッセージリンク先URL
$readup_to_here_not_login_error_link_url = 'http://hogehoge.com/';

#-------------------------------------------------
#  ◎禁止条件部分の外部ファイル化
#-------------------------------------------------

# 禁止条件部分の外部ファイルパス
# 空欄や存在しないファイルパスを指定した時は、本ファイルの設定値を使用します
# 【init.cgiから見たパスを指定して下さい】
my $override_prohibit_settings_filepath = './prohibit-override.cgi';

#===========================================================
#  ◎設定完了
#===========================================================

# 画像拡張子
%imgex = (".jpg" => 1, ".gif" => 1, ".png" => 1);

# 最大で画像6枚のアップロード
# アップロード可能枚数 増加数Validate
$upl_increase_num = int($upl_increase_num);
if ($upl_increase_num > 3) {
	$upl_increase_num = 3;
} elsif ($upl_increase_num < 0) {
	$upl_increase_num = 0;
}

# NGレス置換コメント/エラーメッセージ 文字列のエスケープ
$ngres_comment =~ s/"{1}/\\"/g;
$ngid_error_message =~ s/"{1}/\\"/g;
$ngname_error_message =~ s/"{1}/\\"/g;

# Cookieのキー名の一部に使用するディレクトリパスの取得
$cookie_current_dirpath = do {
	my $dir_separator_regex = quotemeta(File::Spec->canonpath('/'));
	# ドキュメントルートベースのCGI実行パスを取得し、パスをクリーンにする
	my $tmp_dirpath = File::Spec->canonpath(dirname($ENV{'SCRIPT_NAME'}));
	$tmp_dirpath =~ s/(^${dir_separator_regex}?|${dir_separator_regex}?$)//g;
	# 実行パスがjsディレクトリ以下の場合にはWebPatioルートとする
	$tmp_dirpath =~ s/${dir_separator_regex}js(?:${dir_separator_regex}.*)?$//i;
	# URLエンコード
	$tmp_dirpath =~ s/(\W)/'%' . unpack('H2', $1)/eg;
	$tmp_dirpath =~ s/\s/+/g;
	$tmp_dirpath;
};

# 同一条件検索時のreCAPTCHA認証スキップ Cookie暗号化 秘密鍵/公開鍵 空白行除去
$find_recaptcha_continue_cookie_rsa_private_key =~ s/^\s*//;
$find_recaptcha_continue_cookie_rsa_public_key =~ s/^\s*//;

# スレッドログ 保存フォルダ再配置処理 ロックファイルパス
$thread_log_moving_lock_path = "$logdir/moving_threadlog.lock";

# Encode共有インスタンス作成
$enc_cp932 = Encode::find_encoding('cp932');

# 書き込み履歴ログ 記録除外スレッドタイトル 内部エンコード化
@history_save_exempt_titles = map { $enc_cp932->decode($_) } @history_save_exempt_titles;

#-------------------------------------------------
#  アクセス制限
#-------------------------------------------------
sub axscheck {
	# 時間取得
	my $localtime_ref;
	($time, $date, $localtime_ref) = &get_time;
	@localtime = @{$localtime_ref};

	# IP&ホスト取得
	$host = $ENV{'REMOTE_HOST'};
	$addr = $ENV{'REMOTE_ADDR'};

	if ($gethostbyaddr && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}

	# UserAgent取得
    ## _を-に置き換え、,:を除いて取得
	($useragent = $ENV{'HTTP_USER_AGENT'}) =~ tr/_,:/-/d;
    ## 設定値で、文字数の多い順に並び替えし、正規表現エスケープしたリストを取得
    my @ua_remove_strings_regex = map { quotemeta($_); } sort { length($b) <=> length($a) } grep { $_ ne '' } split(/,/, join(',', @useragent_remove_strings));
    if (scalar(@ua_remove_strings_regex) > 0) {
        # マッチパターンを作成し、削除する
        my $match = '(?:' . join('|', @ua_remove_strings_regex) . ')';
        $useragent =~ s/$match//g;
    }

	# IPチェック
	my $flg;
	foreach ( split(/\s+/, $deny_addr) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;

		if ($addr =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		&error("アクセスを許可されていません");

	# ホストチェック
	} elsif ($host) {

		foreach ( split(/\s+/, $deny_host) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			&error("アクセスを許可されていません");
		}
	}
	if ($host eq "") { $host = $addr; }

	## --- 会員制限
	if ($authkey) {
		my $cookie_name = "patio_member_${cookie_current_dirpath}";

		# ログイン
		if ($mode eq "login") {

			# 初期化
			$my_name = "";
			$my_rank = "";

			# 会員ファイルオープン
			my $flg;
			open(IN,"$memfile") || &error("Open Error: $memfile");
			while (<IN>) {
				my ($id,$pw,$rank,$nam) = split(/<>/);

				if ($in{'id'} eq $id) {
					$flg = 1;

					# 照合
					if (&decrypt($in{'pw'},$pw) == 1) {
						$flg = 2;
						$data = "$rank\t$nam";
						$my_name = $nam;
						$my_rank = $rank;
					}
					last;
				}
			}
			close(IN);

			# 照合不可
			if ($flg < 2) { &error("認証できません"); }

			# セッションID発行
			my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
			my $cookid;
			srand;
			foreach (1 .. 15) {
				$cookid .= $char[int(rand(@char))];
			}

			# セッションID発行
			open(OUT,"+> $sesdir/$cookid.cgi");
			print OUT "$in{'id'}\t$time\t$data";
			close(OUT);

			# セッションクッキー埋め込み
			print "Set-Cookie: $cookie_name=$cookid;\n";

			# クッキーID＆ログインID
			$my_ckid = $cookid;
			$my_id   = $in{'id'};

		# ログイン中
		} else {

			# クッキー取得
			my $cook = $ENV{'HTTP_COOKIE'};

			# 該当IDを取り出す
			my %cook;
			foreach ( split(/;/, $cook) ) {
				my ($key,$val) = split(/=/);
				$key =~ s/\s//g;

				$cook{$key} = $val;
			}

			# セッションID有効性をチェック
			if ($cook{$cookie_name} !~ /^[a-zA-Z0-9]{15}$/ || !-e "$sesdir/$cook{$cookie_name}.cgi") {
				&enter_disp;
			}

			# セッションファイル読み取り
			open(IN,"$sesdir/$cook{$cookie_name}.cgi");
			my $ses_data = <IN>;
			close(IN);

			my ($id,$tim,$rank,$nam) = split(/\t/, $ses_data);

			# 時間チェック
			if ($time - $tim > $authtime * 60) {

				unlink("$sesdir/$cook{$cookie_name}.cgi");
				print "Set-Cookie: $cookie_name=;\n";

				my $msg = qq|ログイン有効時間を経過しました。再度ログインしてください。<br>\n|;
				$msg .= qq|<a href="$bbscgi?mode=enter_disp">【再ログイン】</a>\n|;

				&error($msg);
			}

			# 名前＆クッキーID＆ログインID
			$my_name = $nam;
			$my_ckid = $cook{$cookie_name};
			$my_id   = $id;
			$my_rank = $rank;
		}
	}
}

#-------------------------------------------------
#  フォームデコード
#-------------------------------------------------
sub parse_form {
	undef(%in);
	undef(%fname);
	undef(%uplno);
	undef(%ctype);
	$macbin = 0;
	$postflag = 0;

	# 複数同じnameで送られてきた場合に、最後の送信値を取得するname
	my @last_value_get_keys = ('save_history', 'increase_num');

	# マルチパートフォームのとき
	if ($image_upl && $ENV{'CONTENT_TYPE'} =~ m|multipart/form-data|i) {
		$postflag = 1;

		# 添付ファイル最大数
		my $max_upl_num = 3 + $upl_increase_num;

		# 変数初期化
		local($bound,$key,$val);

		# 標準入力をバイナリモード宣言
		binmode(STDIN);

		# 先頭のboundaryを認識
		$bound = <STDIN>;
		$bound =~ s/\r\n//;

		# 標準入力を展開
		while (<STDIN>) {

			# マックバイナリ認識
			if (m|application/x-macbinary|i) { $macbin = 1; }

			# Content-Disposition認識
			if (/^Content-Disposition:/i) {
				$flg = 1;
			}

			# name属性認識
			if ($flg == 1 && /\s+name="([^";]+)"/i) {
				$key = $1;

				if ($key =~ /^upfile([1-$max_upl_num])$/) {
					$uplno = $1;
					$uplno{$uplno} = $uplno;
				}
			}

			# filename属性認識（ファイルアップ）
			if ($uplno && /\s+filename="([^";]+)"/i) {
				$fname{$uplno} = $1;
			}

			# Content-Type認識（ファイルアップ）
			if ($uplno && /Content-Type:\s*([^";]+)/i) {
				my $ctype = $1;
				$ctype =~ s/\r//g;
				$ctype =~ s/\n//g;

				$ctype{$uplno} = $ctype;
			}

			# ヘッダ → 本文
			if ($flg == 1 && /^\r\n/) {
				$flg = 2;
				next;
			}
			# 本文認識
			if ($flg == 2) {
				# boundary検出 → フィールド終了
				if (/^$bound/) {
					# 末尾の改行をカット
					$val =~ s/\r\n$//;

					# テキスト系は改行を変換
					if (!$uplno) {

						# S-JISコード変換
						&jcode::convert(\$val, 'sjis');

						# エスケープ
						$val =~ s/&/&amp;/g;
						$val =~ s/"/&quot;/g;
						$val =~ s/</&lt;/g;
						$val =~ s/>/&gt;/g;

						# 本文およびNGワード・NGスレッドワード設定時以外は改行コードを除去
						if ($key ne "comment" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words') {
						$val =~ s/\r|\n//g;
						} 
						
						# プレビュー時およびNGワード・NGスレッドワード設定時は改行を置換しない
						if ($in{'mode'} ne "preview" && $in{'mode'} ne "resview" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words') {
#						} else {
#						if ($in{'mode'} eq "regist") {
						$val =~ s/\r\n/<br>/g;
						$val =~ s/\r/<br>/g;
						$val =~ s/\n/<br>/g;
						}
					}

					# ハッシュ化
					if (exists($in{$key}) && scalar(grep { $_ eq $key } @last_value_get_keys) > 0) {
						# 同じnameが送信されてきた場合に、最後の送信値を取得するname
						$in{$key} = $val;
					} else {
						$in{$key} .= "\0" if (defined($in{$key}));
						$in{$key} .= $val;
					}

					# フラグを初期化
					$flg = $uplno = $key = $val = '';
					next;
				}
				# boundary検出まで本文を覚えておく
				$val .= $_;
			}
		}

	# マルチパートフォーム以外のとき
	} else {

		my $buf;
		if ($ENV{'REQUEST_METHOD'} eq "POST") {
			$postflag = 1;
			read(STDIN, $buf, $ENV{'CONTENT_LENGTH'});
		} else {
			$buf = $ENV{'QUERY_STRING'};
		}
		foreach ( split(/&/, $buf) ) {
			my ($key, $val) = split(/=/);
			$val =~ tr/+/ /;
			$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

			# S-JISコード変換
			&jcode::convert(\$val, 'sjis');

			# エスケープ
			$val =~ s/&/&amp;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;

						# 本文およびNGワード・NGスレッドワード設定時以外は改行コードを除去
						if ($key ne "comment" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words' && $in{'mode'} ne 'admin') {
						$val =~ s/\r|\n//g;

						} 

						# プレビュー時およびNGワード・NGスレッドワード設定時は改行を置換しない
						if ($in{'mode'} ne "preview" && $in{'mode'} ne "resview" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words' && $in{'mode'} ne 'admin')  {
			$val =~ s/\r\n/<br>/g;
			$val =~ s/\r/<br>/g;
			$val =~ s/\n/<br>/g;
			}
			
			# ハッシュ化
			if (exists($in{$key}) && scalar(grep { $_ eq $key } @last_value_get_keys) > 0) {
				# 同じnameが送信されてきた場合に、最後の送信値を取得するname
				$in{$key} = $val;
			} else {
				$in{$key} .= "\0" if (defined($in{$key}));
				$in{$key} .= $val;
			}
		}
	}
	$in{'sub'} .= $in{'add_sub'} if(defined($in{'add_sub'}));
	$mode = $in{'mode'};
	$p = $in{'p'};
	$i_nam = $in{'name'};
	$i_sub = $in{'sub'};
	$i_com = $in{'comment'};
	$headflag = 0;
	$l = $in{'l'};

	# カテゴリ表示機能 カテゴリ文字列バリデーション
	if ($in{'k'} ne '') {
		# 半角英小文字・数字(1～9)以外が含まれていた場合、機能を無効にする
		if ($in{'k'} =~ /[^a-z1-9]/) {
			delete($in{'k'});
		} else {
			# 機能が有効の場合には先頭10文字を切り出し、それ以降を切り捨てる
			$in{'k'} = substr($in{'k'}, 0, 10);
		}
	}

	# スレッドログ 保存フォルダ再配置処理検知
	# 再配置処理ロックファイルが存在するときは、処理中の可能性があるため
	# スレッドログファイル破損防止のため、
	# 管理画面以外の表示が要求された際に、エラー表示を行います
	if (basename($ENV{SCRIPT_NAME}) ne basename($admincgi) && -e $thread_log_moving_lock_path) {
		error('メンテナンス中につき表示できません');
	}
}

#-------------------------------------------------
#  HTMLヘッダ
#-------------------------------------------------
sub header {
	my ($sub, $js, $disable_buffering) = @_;

	if ($sub ne '') { $title = $sub; }

	if ($disable_buffering) {
		# 標準出力のオートフラッシュを有効化 (バッファリング無効化)
		local $| = 1;
	}

	print "Content-type: text/html\n\n";

	if ($disable_buffering) {
		# ブラウザでは256byte受信しないとレンダリングを開始しないため、半角スペースを出力
		for (my $i=0; $i<256; $i++) {
			print ' ';
		}
	}

	print <<"EOM";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
EOM
	if((caller 1)[3] =~ /^.*::find$/) { 
		print "<link rel=\"stylesheet\" href=\"https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css\">\n";
	}
	print <<"EOM";
<style type="text/css">
<!--
body,td,th { font-size:$b_size;	font-family:$b_face; }
a:hover { color:$al }
.num { font-size:12px; font-family:Verdana,Helvetica,Arial; }
.s1  { font-size:10px; font-family:Verdana,Helvetica,Arial; }
.s2  { font-size:10px; font-family:"$b_face"; }
a.ng_toggle:link    { text-decoration: none;      color: #00F; }
a.ng_toggle:visited { text-decoration: none;      color: #00F; }
a.ng_toggle:hover   { text-decoration: underline; color: #00F; }
a.ng_toggle:active  { text-decoration: none;      color: #00F; }
a.ng_toggle.enabled { color: #ff0002; }
.link_name2 { background-color:#ffe731; }
span.link_name1.ng_res, span.link_name2.ng_res { color: #a5a5a5; }
span[class^="hatugen_"].ngres_count { color: #a5a5a5; }
div.refRes { margin: 20px 0px 0px 20px; }
tbody#genkoulog { background-color: #ffff00; }
tbody#kakolog { background-color: #e2efda; ]
-->
</style>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
EOM

	# JavaScript
	if ($js eq "js") {
		print "<Script Language=\"JavaScript\">\n<!--\n";
		print "function MyFace(Smile) {\n";
		print "myComment = document.myFORM.comment.value;\n";
		print "document.myFORM.comment.value = myComment + Smile;\n";
		print "}\n//-->\n</script>\n";
	}

	# IE7以下でもJSONを使用できるようにする
    print <<"EOM";
<!--[if lte IE 7]>
	<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/json3/3.3.2/json3.min.js"></script>
<![endif]-->
EOM

	# NGID/NGネーム/NGワード/連鎖NG機能
    if((caller 1)[3] =~ /^.*::view$/) {
        # 設定出力
        print "<script type=\"text/javascript\" src=\"js/config.min.js.cgi\"></script>\n";
        # NGID/NGネーム/NGワード/連鎖NG機能
        # 被参照レス件数表示・展開表示機能
        # print "<script type=\"text/javascript\" src=\"js/read.min.js\"></script>\n";
        print "<script type=\"text/javascript\" src=\"js/_original/read.js\"></script>\n";
		# スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能
		# スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能
		print "<script type=\"text/javascript\" src=\"js/read_prohibit.min.js\"></script>\n";
	}

	# 新規スレッド作成フォーム・レスフォーム・ユーザー間メール送信フォームで使用するJavaScriptファイル
	# プライベートブラウジングモード判定
	# フォーム submitボタン制御
	if ((caller 1)[3] =~ /^.*::(?:form|view|mailform)$/) {
		print "<script type=\"text/javascript\" src=\"js/pm.min.js\"></script>\n";
		print "<script type=\"text/javascript\" src=\"js/form.min.js\"></script>\n";
	}

	# 新規スレッド作成フォーム・レスフォーム
	# フォーム 「3枚以上アップロードする」制御
	if ((caller 1)[3] =~ /^.*::(?:form|view)$/) {
		print "<script type=\"text/javascript\" src=\"js/upload.min.js\"></script>\n";
	}

	# ワード検索 検索項目 表示状態設定
	if((caller 1)[3] =~ /^.*::find$/) {
		print <<"EOM";
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1/i18n/jquery.ui.datepicker-ja.min.js"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js"></script>
<script type="text/javascript">
	// input type=date fallback
	\$(function() {
		if(!Modernizr.inputtypes.date) {
			\$('input[type=date]').datepicker({
				dateFormat: 'yy-mm-dd',
				beforeShow: function(input, inst) {
					setTimeout(function() {
						input = \$(input);
						inst.dpDiv.css({
							top: input.offset().top + input.height() + (inst.dpDiv.outerHeight() - inst.dpDiv.height()),
							left: input.offset().left
						});
					}, 0);
				}
			});
		}
	});

	// define find item block utility function
	var findItem = new (function() {
		// update display state
		this.updateDisplayState = function() {
			if(\$("input[name='type']").first().prop("checked")) {
				\$("#findItem").show();
			} else {
				\$("#findItem").hide();
			}
		}
		// add onLoad event
		\$(function() {
			// set onClick update event
			\$("input[name='type']").click(findItem.updateDisplayState);
			// update display state
			findItem.updateDisplayState();
		});
	})();
</script>
EOM
	}

	if((caller 1)[3] =~ /^.*::history_list_view$/) {
		print "<script type=\"text/javascript\" src=\"js/history.min.js\"></script>\n";
	}

	print "<title>$title</title></head>\n";

	# bodyタグ
	if ($bg) {
		print qq|<body background="$bg" bgcolor="$bc" text="$tx" link="$lk" vlink="$vl" alink="$al">\n|;
	} else {
		print qq|<body bgcolor="$bc" text="$tx" link="$lk" vlink="$vl" alink="$al">\n|;
	}
	$headflag = 1;
}

#-------------------------------------------------
#  処理成功メッセージ
#-------------------------------------------------
sub success {
	my ($message, $back_url) = @_;

	chomp($back_url);
	if ($back_url eq '') {
		$back_url = 'history.back()';
	} else {
		$back_url = "location.href='$back_url'";
	}

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>SUCCESS</h3>
<p>$message</p>
<p>
<form>
<input type="button" value="前画面にもどる" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  エラー処理
#-------------------------------------------------
sub error {
    my ($message, $back_url) = @_;

    chomp($back_url);
    if($back_url eq '') {
        $back_url = 'history.back()';
    } else {
        $back_url = "location.href='$back_url'";
    }

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>ERROR !</h3>
<p><font color="red">$message</font></p>
<p>
<form>
<input type="button" value="前画面にもどる" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

sub success {
	my ($message, $back_url) = @_;

	chomp($back_url);
	if($back_url eq '') {
		$back_url = 'history.back()';
	} else {
		$back_url = "location.href='$back_url'";
	}

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>SUCCESS !</h3>
<p><font>$message</font></p>
<p>
<form>
<input type="button" value="前画面にもどる" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#check image type
sub check_imagetype {
	# checks file contents

	my ($data) = @_;
	if ($data =~ m[^\x89PNG]) {
		return q{image/x-png};
	}
	if (length $data > 1) {
		$substr = substr($data, 1, 1024);
		if (defined $substr && $substr =~ m[^PNG]) {
			return q{image/x-png};
		}
	}
	if (length $data > 0) {
		$substr = substr($data, 0, 2);
		if (pack('H*', 'ffd8') eq $substr) {
			return q{image/jpeg};
		}
	}
	if ($data =~ m[^GIF8]) {
		return q{image/gif};
	}

	if ($data =~ m[^hsi1]) {
		return q{image/x-jpeg-proprietary};
	}
}

#-------------------------------------------------
#  時間取得
#-------------------------------------------------
sub get_time {
	$ENV{'TZ'} = "JST-9";
	my $time = time;
	my @localtime = localtime($time);
#	my ($min,$hour,$mday,$mon,$year) = (localtime($time))[1..5];
	my ($sec,$min,$hour,$mday,$mon,$year) = @localtime[0..5];

	# 日時のフォーマット
#	my $date = sprintf("%04d/%02d/%02d %02d:%02d", $year+1900,$mon+1,$mday,$hour,$min);
	my $date = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$mon+1,$mday,$hour,$min,$sec);
	return ($time, $date, \@localtime);
}

#-------------------------------------------------
#  入室画面
#-------------------------------------------------
sub enter_disp {
	&header;
	print <<EOM;
<div align="center">
<table><tr><td>
・ 入室にはログインIDとパスワードが必要です。<br>
・ ブラウザのクッキーは必ず有効にしてください。
</td></tr></table>
<form action="$bbscgi" method="post">
<input type="hidden" name="mode" value="login">
<Table border="0" cellspacing="0" cellpadding="0" width="200">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center">ログインID</td>
  <td bgcolor="$col2" nowrap><input type="text" name="id" value="" size="20" style="width:160px"></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center">パスワード</td>
  <td bgcolor="$col2" nowrap><input type="password" name="pw" value="" size="20" style="width:160px"></td>
</tr>
</table>
</Td></Tr></Table>
<p></p>
<input type="submit" value="ログイン" style="width:80px">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  スレッドログ 保存フォルダ番号取得
#-------------------------------------------------
sub get_logfolder_number {
	my ($thread_number) = @_;

	if ($number_in_threadlog_folder >= 1) {
		# $thread_numberは1始まり、スレッドログフォルダも1始まり
		# 5桁にゼロパディングする
		return sprintf('%05d', ((($thread_number - 1) / $number_in_threadlog_folder) + 1));
	} else {
		return;
	}
}

#-------------------------------------------------
#  スレッドログ 保存フォルダパス取得
#-------------------------------------------------
sub get_logfolder_path {
	my ($thread_number) = @_;

	my $thread_logfolder_number = get_logfolder_number($thread_number);
	if (defined($thread_logfolder_number)) {
		return "$logdir/$thread_logfolder_number";
	} else {
		# 1未満を設定してる場合は、従来の$logdir直下を返す
		return $logdir;
	}
}

#-------------------------------------------------
#  crypt暗号
#-------------------------------------------------
sub encrypt {
	my ($inpw) = @_;

	# 文字列定義
	my @char = ('a'..'z', 'A'..'Z', '0'..'9', '.', '/');

	# 乱数で種を生成
	srand;
	my $salt = $char[int(rand(@char))] . $char[int(rand(@char))];

	# 暗号化
	crypt($inpw, $salt) || crypt ($inpw, '$1$' . $salt);
}

#-------------------------------------------------
#  crypt照合
#-------------------------------------------------
sub decrypt {
	my ($inpw, $enpw) = @_;

	if ($enpw eq "") { &error("認証できません"); }

	# 種抜き出し
	my $salt = $enpw =~ /^\$1\$(.*)\$/ && $1 || substr($enpw, 0, 2);

	# 照合処理
	if (crypt($inpw, $salt) eq $enpw || crypt($inpw, '$1$' . $salt) eq $enpw) {
		return 1;
	} else {
		return 0;
	}
}


#--------------#
#  ID生成処理  #
#--------------#

sub makeid {
	my $idnum = substr($addr, 8) ** 2;

	my @salt_charlist = ('.', 'A'..'Z', '/', 'a'..'z', 0..9);
	my $localtime = timegm(localtime($time)); # 0時に切り替わるよう、GMTからの時差を含めてエポック経過秒数に変換する
	my $cycle_day = $localtime / 86400 % (scalar(@salt_charlist) ** 2); # salt使用可能文字^salt2文字を1サイクルとして、サイクル中の日数をエポックからの日数の剰余で計算
	my $salt = join('', @salt_charlist[int($cycle_day/scalar(@salt_charlist)), $cycle_day%scalar(@salt_charlist)]);

	$idcrypt = substr(crypt($idnum, $salt), -8);
}

#---------------------------------------
#  トリップ機能
#---------------------------------------
sub trip {
	my ($name) = @_;
	#入力した名前欄の文字列がそのまま記録されます。
	return $name;
	$name =~ s/◆/◇/g;

	if ($name =~ /#/) {
		my ($handle,$trip) = split(/#/, $name, 2);

#		local($enc) = crypt($trip, $trip_key) || crypt ($trip, '$1$' . $trip_key);
#		$enc =~ s/^..//;

		# 2ch互換トリップ
		my ($trip_key) = substr(substr($trip,0,8).'H.', 1, 2);
		$trip_key =~ s/[^\.-z]/\./go;
		$trip_key =~ tr/:;<=>?@[\\]^_`/ABCDEFGabcdef/;
		my ($enc) = substr(crypt($trip, $trip_key), -10);

		return "$handle◆$enc";
	} else {
		return $name;
	}
}

#-------------------------------------------------
#  クッキー取得
#-------------------------------------------------
sub get_cookie {
	# 該当IDを取り出す
	my %cook;
	foreach my $set (split(/;/, $ENV{'HTTP_COOKIE'})) {
		my ($key, $val) = split(/=/, $set);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# データをURLデコードして復元
	my @cook;
	my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}";
	foreach my $val (split(/<>/, $cook{$cookie_name})) {
		$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		push(@cook, $val);
	}
	return @cook;
}

#-------------------------------------------------
#  Google AdSense
#-------------------------------------------------
sub googleadsense {

	if ($adsenseenable) {

# ここにGoogle AdSenseのコードを貼ることができます。
	print <<"EOM";
EOM

	}

}

#--------------------------#
#  管理画面でのinit.cgi設定  #
#    変数オーバーライド処理     #
#--------------------------#
# 処理中の変数名がdefault_で始まる変数は
# 管理画面内動作設定でinit.cgiの
# 設定値を取得するために使用します
if($conf_override) {
	# オーバーライド設定ファイルが存在するときは読み込む
	if(-f $conf_override_path) {
		require "$conf_override_path";
	}

	# サムネイル画像サイズ
	$default_img_max_w = $img_max_w;
	$default_img_max_h = $img_max_h;
	if(defined $override_img_max_w && defined $override_img_max_h) {
		if($override_img_max_w =~ /^\d+$/ && $override_img_max_h =~ /^\d+$/) {
			$img_max_w = $override_img_max_w;
			$img_max_h = $override_img_max_h;
		}
	}

	# サムネイル画像生成サイズ
	$default_thumb_max_w = $thumb_max_w;
	$default_thumb_max_h = $thumb_max_h;
	if(defined $override_thumb_max_w && defined $override_thumb_max_h) {
		if($override_thumb_max_w =~ /^\d+$/ && $override_thumb_max_h =~ /^\d+$/) {
			$thumb_max_w = $override_thumb_max_w;
			$thumb_max_h = $override_thumb_max_h;
		}
	}

	# アップロード可能ファイル拡張子
	%default_imgex;
	while(my ($key,$value) = each(%imgex)) {
		$default_imgex{lc $key} = $value;
	}
	%imgex = %default_imgex;
	if(%override_imgex) {
		while(my ($key,$value) = each(%override_imgex)) {
			if($value =~ /[01]{1}/) {
				$imgex{lc $key} = $value;
			}
		}
	}
	my $enableExtCount = 0;
	$enableExtCount += $_ for values(%imgex);
	if($enableExtCount == 0) {
		# アップロード可能ファイル拡張子が一つもないときは、アップロード機能を停止
		$image_upl = 0;
	}
}

#-----------------------------------
#  禁止条件部分の外部ファイルによる
#  変数オーバーライド処理
#-----------------------------------
if (defined($override_prohibit_settings_filepath) && -f $override_prohibit_settings_filepath) {
	# WebPatioProhibitOverrideConfパッケージ下で外部ファイルロード
	package WebPatioProhibitOverrideConf;
	require "$override_prohibit_settings_filepath";

	# 指定した名前の変数・配列のみ読み込みを行う
	my @scalar_name_array = ('no_wd', 'ng_nm');
	my @array_name_array = (
		'duplicate_post_restrict_thread', 'hide_form_name_field', 'remove_name_on_post',
        'permit_name_regex', 'contents_branching_keyword', 'prohibit_img_md5hash',
		'firstpost_restrict_exempt',
		'disable_img_upload', 'disable_age', 'thread_browsing_restrict_user',
		'auto_post_prohibit_combination_imgmd5', 'auto_post_prohibit_multiple_submissions', 'auto_post_prohibit_old_thread_age'
	);
	for (my $i = 1; $i <= 20; $i++) {
		# スレッドタイトル自動書き込み禁止機能のレス部分相当で動作する機能
		# レス内容 制限単語設定・制限除外単語設定
		if ($i == 1) {
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_keyword");
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword");
		} else {
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_keyword_$i");
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_$i");
		}
	}
	foreach my $scalar_name (@scalar_name_array) {
		$main::{$scalar_name} = $WebPatioProhibitOverrideConf::{$scalar_name};
	}
	foreach my $array_name (@array_name_array) {
		@main::{$array_name} = @WebPatioProhibitOverrideConf::{$array_name};
	}

	# WebPatioProhibitOverrideConfパッケージを削除
	Symbol::delete_package('WebPatioProhibitOverrideConf');
}

# スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能
# 設定値を配列に
@auto_post_prohibit_thread_title_res_target_restrict_keyword_array = (
	$auto_post_prohibit_thread_title_res_target_restrict_keyword,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_2,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_3,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_4,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_5,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_6,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_7,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_8,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_9,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_10,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_11,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_12,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_13,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_14,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_15,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_16,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_17,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_18,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_19,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_20
);
@auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_array = (
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_2,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_3,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_4,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_5,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_6,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_7,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_8,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_9,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_10,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_11,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_12,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_13,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_14,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_15,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_16,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_17,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_18,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_19,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_20
);
@auto_post_prohibit_thread_title_res_target_hold_hour_array = (
	$auto_post_prohibit_thread_title_res_target_hold_hour_1,
	$auto_post_prohibit_thread_title_res_target_hold_hour_2,
	$auto_post_prohibit_thread_title_res_target_hold_hour_3,
	$auto_post_prohibit_thread_title_res_target_hold_hour_4,
	$auto_post_prohibit_thread_title_res_target_hold_hour_5,
	$auto_post_prohibit_thread_title_res_target_hold_hour_6
);

1;
