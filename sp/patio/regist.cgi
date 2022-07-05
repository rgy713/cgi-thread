#!/usr/bin/perl

#┌─────────────────────────────────
#│ [ WebPatio ]
#│ regist.cgi - 2011/07/06
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# きりしま式 K1.10
# 2014/08/10 スレッドの連続作成、レスの連続投稿の処理ルーチンの変更
# 2013/03/03 過去ログのバグ修正
# 2012/09/08 過去ログのバグ修正
# 2011/07/06 3.4相当に修正
# 2010/06/23 新規スレッド作成とレスのタイマーを分けてみました
# 2010/01/11 禁止ワードに引っかかったキーワードをレポートするように
# 2009/07/06 sub deleteは使ってない模様なのでソースコードを削除
#            記事の削除時にレスの数をカウントし直すように変更
# 2009/06/23 記事閲覧画面のスパナから入ったときに親記事を分割（コピー）できなかったバグの修正
# 2009/06/15 レス数を計算している部分で数え直せる機会には数え直すように修正
# 2009/06/01 ユーザー間メール機能を無効にできるように
# 2009/05/18 メール送信機能の控えで差出人名が化けるバグの修正
# 2009/03/28 FAQモード
# 2009/03/14 スレッド作成制限モードの追加
# 2009/01/12 禁止語フィルタにURL欄も適用
# 2008/12/22 3.22相当に修正
# 2008/08/29 いったん一式アーカイブを更新
# 2008/04/28 スレッドの最後の記事を削除すると最終アクセス時間が削除される記事の時間になってしまうバグの修正
# 2008/02/27 スレッド分割機能を装備（厳密には指定レス以降をコピーして新規スレッド作成）
# 2008/01/15 レスお知らせメールのルーチン組み込み
# 2008/01/09 過去ログに落ちてても書き込みができるセキュリティ上の問題に対処
# 2007/06/25 レスを削除してレス数が0になるときに、レスタイトルが親記事のタイトルになるのを修正
# 2007/06/10 3.2相当に修正
# 2007/05/01 ユーザーの記事削除時にレス数調整。レスが0になるときの表示修正
# 2007/04/06 スレッドトップの記事から、管理者パスで直接スレッド削除ができるフォームを設置
# 2007/03/06 2ch互換トリップ

# 外部ファイル取り込み
BEGIN {
	require './init.cgi';
	require $jcode;
	eval "use lib '$webprotect_path/lib'";
	eval 'use WebProtectAuth';
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HTML::Entities qw();
use ThreadUpdateLogDB;
use LWP::UserAgent;
use JSON::XS;
use URI;
use File::Spec;
use POSIX qw/strftime/;
use UniqueCookie;
use List::MoreUtils;
use HistoryCookie;
use HistoryLog;
use FirstCookie;
use MIME::Base64;
use AutoPostProhibit;
use ThreadCreatePostRestrict;
use Matcher::Utils;
use Matcher::Variable;
no encoding;

&parse_form;
&axscheck;

# Matcher::Utils インスタンス初期化
# ($mode が "regist" もしくは "mailsend" のときのみ初期化する)
# (内部で Matcher::Variable インスタンスを初期化してセット)
my Matcher::Utils $mu;
if ($mode eq "regist" || $mode eq "mail") {
	$mu = Matcher::Utils->new(
		$time,
		$enc_cp932,
		$match_hiragana_katakana_normalize_mode,
		Matcher::Variable->new($match_variable_settings_filepath),
		\&trip,
		$restrict_user_from_thread_page_target_log_path,
		$restrict_user_from_thread_page_target_hold_hour_1,
		$restrict_user_from_thread_page_target_hold_hour_2,
		$restrict_user_from_thread_page_target_hold_hour_3,
		$restrict_user_from_thread_page_target_hold_hour_4,
		$restrict_user_from_thread_page_target_hold_hour_5,
		$restrict_user_from_thread_page_target_hold_hour_6,
		$restrict_user_from_thread_page_target_hold_hour_7,
		$restrict_user_from_thread_page_by_time_range_target_log_path,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_1,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_2,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_3,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_4,
		$restrict_user_from_thread_page_by_time_range_enable_time_range,
		$in_thread_only_restrict_user_from_thread_page_target_log_path,
		$in_thread_only_restrict_user_from_thread_page_target_hold_hour
	);
}

if ($mode eq "regist") { &regist; }
elsif ($mode eq "del") { &delete; }
elsif ($mode eq "mente") { &mente; }
elsif ($mode eq "edit_log") {
	require $editlog;
	&edit_log;
}
elsif ($mode eq "mail") { &mailsend; }
&error("不明な処理です");

#-------------------------------------------------
#  記事投稿処理
#-------------------------------------------------
sub regist {
	local (%fn, %ex, %image_orig_md5, %image_conv_md5);

	#「スレッドを生成」をクリック時、「確認」にチェックが入っていない場合はエラー画面を表示します。
	# プレビュー機能を有効（$restitle = 0;）にした場合は、チェックボックスを表示しません。
	if ($restitle && $in{'res'} eq ''){
		if( $in{'confirm'} ne 'on') {
			error("確認をチェックして下さい。");
		}
	}

	# 権限チェック
	if ($authkey && $my_rank < 2) {
		&error("投稿の権限がありません$my_rank");
	}

	# POST限定
	if ($postonly && !$postflag) { &error("不正なアクセスです"); }

	# 汚染チェック
	$in{'res'} =~ s/\D//g;

	# 現行スレッドindexファイルオープン
	open(my $nowfile_fh, '+<', $nowfile) || &error("Open Error: $nowfile");
	flock($nowfile_fh, 2) || error("Lock Error: $nowfile");

	# 自動書き込み禁止機能の除外時URL欄のための、新規スレッド スレッドNo採番
	my $new;
	{
		my $top = <$nowfile_fh>;
		my ($no) = split(/<>/, $top);
		$new = $no + 1; # 新規作成時 スレッド番号採番
		seek($nowfile_fh, 0, 0); # ファイルポインタを戻す
	}

	# フォームから送信されたプライベートブラウジングモードであるかどうかの情報を取得
	my $is_private_browsing_mode = (exists($in{'pm'}) && $in{'pm'} eq '1') ? 1 : 0;

	# ユニークCookieAインスタンスを作成
	my $cookie_a = UniqueCookie->new($cookie_current_dirpath);

	# Cookieに保存されている登録IDを取得
	my $user_id_on_cookie = do {
		my @cookies = get_cookie();
		$cookies[5] || '';
	};

	# 書込IDを取得
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};

	# 返信レスはログ記録以外スレッドタイトルをタイトルとする
	my $log_fh;
	my %first_res;
	my $file = '';
	my @log;
	my $newno = 0;
	if ($in{'res'} ne '') {
		# ファイルオープン
		# (他の箇所でもファイルハンドル使用するため、排他ロックしてオープンしたままとする)
		my $logfile_path = get_logfolder_path($in{'res'}) . "/$in{'res'}.cgi";
		open($log_fh, '+<', $logfile_path) || error("Open Error: $in{'res'}.cgi");
		flock($log_fh, 2) || error("Lock Error: $in{'res'}.cgi");
		seek($log_fh, 0, 0);

		# スレッドログ読み込み
		my $loaded_lines = 0;
		while (my $log_line = <$log_fh>) {
			# 書き込み時のために、生ログデータを保管 (ヘッダー行を除く)
			if ($loaded_lines > 0) {
				$file .= $log_line;
			}
			chomp($log_line);
			my @res_log = split(/<>/, $log_line);
			if ($loaded_lines == 0) {
				# スレッドタイトル取得
				$i_sub = $res_log[1];

				# レス番号採番
				my $res = $res_log[2];
				if ($res == 0) {
					$newno = 2;
				} else {
					$newno = $res + 1;
				}
			} elsif ($loaded_lines == 1) {
				# >>1の取得
				# スレッドタイトルによる書き込み制限機能のスレッド作成者の除外機能
				# >>1の ホスト, URL欄, 登録ID, CookieA, 書込ID を取得
				(my $valid_history_id = $res_log[20]) =~ s/\@$//;
				%first_res = (
					'host'       => $res_log[6],
					'url'        => $res_log[8],
					'user_id'    => $res_log[16],
					'cookie_a'   => $res_log[18],
					'history_id' => $valid_history_id,
				);
			}
			# ログ配列に追加
			push(@log, \@res_log);
			$loaded_lines++;
		}

		# ファイルポインタを先頭に戻す
		seek($log_fh, 0, 0);
	}

	# スレッドタイトル判定用変数(カテゴリ名を除く)
	my $check_i_sub = $i_sub;
	if (defined($in{'add_sub'})) {
		$check_i_sub =~ s/\Q${in{'add_sub'}}\E$//;
	}

	# 初回Cookieインスタンス初期化
	my $first_cookie = FirstCookie->new(
		$mu,
		$firstpost_restrict_settings_filepath,
		$time, $host, $useragent, $cookie_a, $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
		$cookie_current_dirpath, \@firstpost_restrict_exempt
	);

	# 初回書き込みまでの時間制限機能
	{
		# 判定
		my $type = $in{'res'} eq '' ? FirstCookie::THREAD_CREATE : FirstCookie::RESPONSE;
		$first_cookie->judge_and_update_cookie($type, $check_i_sub);

		# 制限時間取得
		my $left_hours = $first_cookie->get_left_hours_of_restriction();
		if ($left_hours > 0) {
			my $post_type = $in{'res'} eq '' ? 'スレッド作成' : 'レス';
			my $restrict_hours = $first_cookie->get_hours_of_restriction();
			my $back_url = $ENV{'HTTP_REFERER'} || ($in{'res'} eq '' ? "$readcgi?mode=form" : "$readcgi?no=$in{'res'}");
			error("${post_type}が可能\になるまであと${left_hours}時間です。●${restrict_hours}", $back_url);
		}
	}

	# 名前欄非表示機能 (返信レス時のみ)
	my $is_hide_name_field_in_form = $in{'res'} ne '' && $mu->is_hide_name_field_in_form($check_i_sub, \@hide_form_name_field);
	if ($is_hide_name_field_in_form) {
		# 対象スレッドの場合は、送られてきた値にかかわらず、名前を空値とする
		$i_nam = '';
	}

	# チェック
	if ($no_wd) { &no_wd; }
	if ($jp_wd) { &jp_wd; }
	if ($urlnum > 0) { &urlnum; }

	# コメント文字数チェック
	if (length($i_com) > $max_msg*2) {
		&error("文字数オーバーです。<br>全角$max_msg文字以内で記述してください");
	}

	# 外部ファイルによるスレッド作成制限機能などの統合 インスタンス初期化
	my $thread_create_post_restrict = ThreadCreatePostRestrict->new(
		$mu,
		$thread_create_post_restrict_settings_filepath,
		$host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
		$cookie_a
	);

	# スレッド作成制限機能
	if ($in{'res'} eq '' ) {
		# 外部ファイルによるスレッド作成制限機能などの統合 スレッド作成制限機能 制限状態取得
		my $thread_create_restrict_status = $thread_create_post_restrict->determine_thread_create_restrict_status();

		if ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # スレッド画面からユーザを制限する機能
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # スレッド画面からユーザを時間制限する機能
		) {
			error('スレッド作成ができません。');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_2) {
			error('スレッド作成ができません。');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_3) {
			error('スレッドの作成は出来ません。●●');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_4) {
			error('スレッドの作成は出来ません。▲▲');
		} elsif (!$webprotect_auth_new
			&& $thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_5) {
			# 強制的にWebProtectによる登録ID認証を行わせる
			$webprotect_auth_new = 1;
		}
	}

	# スレッドタイトルによる書き込み制限機能(レス投稿時)
	if ($in{'res'} ne '') {
		# 外部ファイルによるスレッド作成制限機能などの統合 スレッドタイトルによる書き込み制限機能 制限状態取得
		my $post_restrict_status = $thread_create_post_restrict->determine_post_restrict_status_by_thread_title(
			$check_i_sub, $first_res{'host'}, $first_res{'url'}, $first_res{'user_id'}, $first_res{'cookie_a'}, $first_res{'history_id'}
		);

		my $msg;
		if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # スレッド画面からユーザを制限する機能
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # スレッド画面からユーザを時間制限する機能
			|| $mu->is_in_thread_only_restricted_user_from_thread_page($in{'res'}, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # スレッド画面からユーザを制限する機能 (そのスレのみ)
		) {
			# 制限対象の場合はエラーメッセージを定義する
			$msg = '書き込みができません。';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2) {
			# 制限対象の場合はエラーメッセージを定義する
			$msg = '書き込みができません。';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3) {
			$msg = 'このスレッドへの書き込みは出来ません。●●';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4) {
			$msg = 'このスレッドへの書き込みは出来ません。▲▲';
		} elsif (!$webprotect_auth_res
			&& $post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5) {
			# 登録ID認証が無効時のみ判定
			# 制限対象の場合はWebProtect認証を有効にする
			$webprotect_auth_res = 1;
		}
		if (defined($msg) && !($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION)) {
			# スレッド作成者以外か、
			# >>1のURL欄にjogaiと指定されていない場合(スレッド作成者の除外機能の対象外)は、
			# エラーメッセージを表示
			error($msg);
		}
	}

	# WebProtect登録ID認証機能 設定状況取得
	my $webprotect_auth = $in{'res'} eq "" ? $webprotect_auth_new : $webprotect_auth_res;

	# アップロードファイル存在判定
	my $upfile_exists = $image_upl && grep { $in{'upfile' . $_} } (1 .. ($in{'increase_num'} ? 3 + $upl_increase_num : 3));

	# ホストなどによる画像アップロードの無効
	$upfile_exists &&= !$mu->is_disable_upload_img($check_i_sub, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode, \@disable_img_upload);

	# 投稿内容チェック
	if ($i_nam eq "") {
		if ($in_name) { &error("名前は記入必須です"); }
		else { $i_nam = '名無し'; }
	}
	if ($in_mail == 1 && $in{'email'} ne "") { &error("E-mailは入力禁止です"); }
	if ($in_mail == 2 && $in{'email'} ne "") { &error("E-mailは入力禁止です"); }
	if ($in_mail == 3 && $in{'email'} ne "") { &error("E-mailは入力禁止です"); }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		&error("E-mailの入力内容が不正です");
	}
	if ($in_url == 1 && $in{'url'} eq "") { &error("URLを必ず入力してください"); }
	if ($in_url == 1 && $in{'url'} eq "http://") { &error("URLを必ず入力してください"); }
	if ($in_url == 2 && $in{'url'} ne "") { &error("URL情報が不正です"); }
	if ($in_url == 3 && $in{'url'} ne "") { &error("URL欄に何か入力してはいけません"); }
	if ($check_i_sub eq "") { &error("タイトルは記入必須です"); }
	if ($check_i_sub =~ /^(\x81\x40|\s)+$/) { &error("タイトルは正しく記入してください"); }
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { &error("名前は正しく記入してください"); }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { &error("コメントは正しく記入してください"); }
	if ($in_pwd && $in{'pwd'} eq "") { &error("パスワードは入力必須です"); }
	if (length($in{'pwd'}) > 8) { &error("パスワードは8文字以内にして下さい"); }
	if ($webprotect_auth && $in{'user_id'} eq "") { &error("登録IDは入力必須です"); }
	if ($webprotect_auth && $in{'user_pwd'} eq "") { &error("登録パスワードは入力必須です"); }
	if ($in{'url'} eq "http://") { $in{'url'} = ""; }
	elsif ($in{url} && $in{url} !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/) {
		&error("URL情報が不正です");
	}

	# 名前欄のNGワード処理
	ng_nm();

	# IDを作成
	if($idkey) { &makeid; }
	else { $idcrypt = "";}

	# ファイルアップ
	local($upl_flg, %w ,%h, %thumb_w, %thumb_h);
	my $upfile_count = 0; # ファイルアップ数
	if ($upfile_exists) {
		require $upload;
		($fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1},
			$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2},
			$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3},
			$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4},
			$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5},
			$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}) = &upload($time, $in{'increase_num'});

		# ファイルアップ数カウント
		$upfile_count = scalar(grep { defined($_) && $_ ne '' } values(%ex));

		# 画像アップのときはフラグを立てる
		if ($upfile_count > 0) { $upl_flg = $time; }
	}

	# ファイルアップ処理後、本文がない場合にエラー表示
	if ($i_com eq "" && $upfile_count == 0) {
		error("コメントの内容がありません");
	}

	# 連続投稿制限比較対象は登録IDであるかどうか
	my $user_id_is_post_limit_comparision_item = ($webprotect_auth && $in{'user_id'}) ? 1 : 0;

	# 連続投稿制限比較対象を決定
	my $postLimitComparisonFirstItem = $user_id_is_post_limit_comparision_item ? $in{'user_id'} : $host;

	# 新規投稿記録ファイルオープン (新規スレッド作成時のみ)
	# ホストなどによるスレッド作成抑制機能で使用するため、先にオープン
	my $threadlog_fh;
	my @threadlog_tmp;
	my $threadlog_same_user_found_for_suppress_thread_creation;
	my $add_to_threadlog;
	if ($in{'res'} eq '') {
		open($threadlog_fh, '+<', $threadlog) || &error("Open Error: $threadlog");
		flock($threadlog_fh, 2) || &error("Lock Error: $threadlog");
		seek($threadlog_fh, 0, 0);

		# 連続投稿IP/登録IDチェック (ファイルハンドルクローズは「新規投稿ログへ記録」の後に行う)
		my $is_same_user;
		while (<$threadlog_fh>) {
			chomp($_);
			if ($_ eq '') {
				next;
			}
			my ($record_host, $record_cookie_a, $record_user_id, $record_history_id, $post_time) = split(/<>/, $_);
			my $passed_wait_thread = $wait_thread < $time - $post_time; # このログ行は$wait_thread秒経過しているかどうか
			# 同一ユーザー判定
			$is_same_user ||=
				!$passed_wait_thread
				&& (
					(!$user_id_is_post_limit_comparision_item && $record_host eq $host)
					|| ($record_cookie_a ne '-' && $record_cookie_a eq $cookie_a->value())
					|| ($user_id_is_post_limit_comparision_item && $record_user_id ne '-' && $record_user_id eq $in{'user_id'})
					|| ($record_history_id ne '-' && $record_history_id eq $chistory_id)
				);
			# ホストなどによるスレッド作成抑制機能のための同一ユーザー判定
			$threadlog_same_user_found_for_suppress_thread_creation ||=
				!$passed_wait_thread
				&& (
					$record_host eq $host
					|| ($record_cookie_a ne '-' && $record_cookie_a eq $cookie_a->value())
					|| ($record_user_id ne '-' && $record_user_id eq $user_id_on_cookie)
					|| ($record_history_id ne '-' && $record_history_id eq $chistory_id)
				);
			if ($is_same_user || $passed_wait_thread) {
				# 同一ユーザーか、$wait_thread経過したログ行はスキップ
				next;
			}
			# 残すログ行を記録配列に追加
			push(@threadlog_tmp, $_);
		}
		if ($is_same_user) {
			# 同一ユーザーで、$wait_threadが経過していないログ行が見つかった時にエラー表示
			close($threadlog_fh);
			&error("連続投稿はもうしばらく時間をおいて下さい");
		}

		# 新規投稿記録ファイル追記サブルーチン定義
		$add_to_threadlog = sub {
			# 新規スレッドの投稿ログを配列の先頭に追加
			my @add_new_thread_log = (
				$host,
				defined($cookie_a->value()) ? $cookie_a->value() : '-',
				exists($in{'user_id'}) && $in{'user_id'} ne '' ? $in{'user_id'} : '-',
				defined($chistory_id) ? $chistory_id : '-',
				$time,
				'' # 最後に<>をつけるためのdummy要素
			);
			unshift(@threadlog_tmp, join('<>', @add_new_thread_log));

			# $hostnum以上の新規スレッド作成ログが存在する場合、末尾を削除
			my $threadlog_excess_elements_count = scalar(@threadlog_tmp) - $hostnum;
			if ($threadlog_excess_elements_count > 0) {
				splice(@threadlog_tmp, $hostnum, $threadlog_excess_elements_count);
			}
			seek($threadlog_fh, 0, 0);
			print $threadlog_fh join("\n", @threadlog_tmp)."\n";
			truncate($threadlog_fh, tell($threadlog_fh));
			close($threadlog_fh);
		};
	}

	# ユニークCookieAを必要に応じて発行
	my $is_cookie_a_issuing = !$cookie_a->is_issued();
	$cookie_a->value(1);

	# 自動書き込み禁止機能
	# ホストなどによるスレッド作成抑制機能
	# 判定実施
	{
		# AutoPostProhibit インスタンス初期化
		my $auto_post_prohibit_instance = AutoPostProhibit->new(
			$mu,
			$prohibit_suppress_settings_filepath, $auto_post_prohibit_log_path, $auto_post_prohibit_no_delete_log_path, $auto_post_prohibit_thread_number_res_target_log_path, $auto_post_prohibit_thread_title_res_target_log_path,
			$auto_post_prohibit_multiple_submissions_count_log_path, $auto_post_prohibit_old_thread_age_count_log_path,
			\@category_convert, $auto_post_prohibit_log_concat_url[0],
			$auto_post_prohibit_exempting_name, \@auto_post_prohibit_additional_match_required_host, $auto_post_prohibit_delete_time, \@auto_post_prohibit_up_to_res_number,
			$auto_post_prohibit_thread_number_res_target_hold_hour_1, $auto_post_prohibit_thread_number_res_target_hold_hour_2, $auto_post_prohibit_thread_number_res_target_hold_hour_3,
			$auto_post_prohibit_thread_number_res_target_hold_hour_4, $auto_post_prohibit_thread_number_res_target_hold_hour_5, $auto_post_prohibit_thread_number_res_target_hold_hour_6,
			\@auto_post_prohibit_thread_title_res_target_restrict_keyword_array, \@auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_array, \@auto_post_prohibit_thread_title_res_target_hold_hour_array,
			\@auto_post_prohibit_combination_imgmd5,
			\@auto_post_prohibit_multiple_submissions, $auto_post_prohibit_multiple_submissions_redirect_threshold, $auto_post_prohibit_multiple_submissions_log_hold_minutes,
			\@ngthread_thread_list_creator_name_override_exclude_hosts,
			\@auto_post_prohibit_old_thread_age, $auto_post_prohibit_old_thread_age_redirect_threshold, $auto_post_prohibit_old_thread_age_log_hold_minutes,
			\@ngthread_thread_list_creator_name_override_exclude_hosts,
			$time, $date, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
			$cookie_a, $is_cookie_a_issuing
		);

		# 判定使用項目
		my $new_thread_flag = $in{'res'} eq '';
		my $thread_no = $in{'res'} eq '' ? $new : int($in{'res'});
		my $age_flag = $in{'sage'} ne '1';
		my $name = $enc_cp932->decode(trip($i_nam)); # トリップ生成後の名前で判定
		my $title = $enc_cp932->decode($i_sub);
		my $res = $enc_cp932->decode($i_com);
		my @image_md5_array_ref_array = map { [ $image_orig_md5{$_}, $image_conv_md5{$_} ] } keys(%fn);

		# 判定実施
		my $result = $auto_post_prohibit_instance->prohibit_post_check(
			$new_thread_flag, $age_flag, $thread_no, $newno, $name, $title, $res, $upfile_count,
			\@image_md5_array_ref_array, $idcrypt, \@log, $threadlog_same_user_found_for_suppress_thread_creation
		);

		# 判定結果によって、スレッド作成抑制、もしくは、リダイレクト処理を行う
		if ($result & AutoPostProhibit::RESULT_THREAD_CREATE_SUPPRESS_REQUIRED) {
			# スレッド作成抑制対象
			$add_to_threadlog->(); # 新規投稿記録ファイルに追記
			error('このスレッドは作成出来ません。');
		} elsif ($result & AutoPostProhibit::RESULT_REDIRECT_REQUIRED && $auto_post_prohibit_redirect_url ne '') {
			# リダイレクト対象
			print "Location: " . URI->new($auto_post_prohibit_redirect_url)->abs($ENV{'REQUEST_URI'}) . "\n\n";
			exit(0);
		}
	}

	# 投稿時の名前の消去機能
	if (is_remove_name_target_post($check_i_sub, $i_nam, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, \@remove_name_on_post)) {
		# 対象の場合に名前を削除し、名前欄空欄時の処理を実行
		$i_nam = '';
		if ($in_name) { &error("名前は記入必須です"); }
		else { $i_nam = '名無し'; }
	}

	# reCAPTCHA認証実施判定
	my ($is_recaptcha_enabled, $create_log_fh, $create_log_no_delete_fh, $auth_host_log_fh) = 0;
	if ($in{'res'} eq '' && ($recaptcha_thread || exists($in{'g-recaptcha-response'}))) {
		# スレッド作成時
		# 消去ログ・累積ログ・reCAPTCHA認証対象ホストログをオープンし、
		# 削除ログが設定件数以上か、reCAPTCHA認証対象ホストに含まれるホスト、
		# もしくは、reCAPTCHAレスポンスが送信されてきた場合に認証を行う
		if (open($create_log_fh, '+>>', $recaptcha_thread_create_log) && flock($create_log_fh, 2) && seek($create_log_fh, 0, 0) # 消去ログオープン
			&& open($create_log_no_delete_fh, '+>>', $recaptcha_thread_create_log_no_delete) && flock($create_log_no_delete_fh, 2) && seek($create_log_no_delete_fh, 0, 0) # 累積ログオープン
			&& open($auth_host_log_fh, '+>>', $recaptcha_thread_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA認証対象ホストログ
			# 消去ログ行数カウント・消去対象行除外
			my $create_log = "日時,スレッドを作成したホスト（または登録ID）,タイムスタンプ\n";
			my $create_count = 0;
			my $is_create_log_changed = 0;
			<$create_log_fh>; # 先頭行読み飛ばし
			while (<$create_log_fh>) {
				chomp($_);
				my @line = split(/,/, $_);
				if (scalar(@line) == 3) {
					# 自動消去が無効か、消去時間が経過していないログのみ残す
					if ($recaptcha_thread_count_time == 0 || ($line[2] + $recaptcha_thread_count_time >= $time)) {
						$create_log .= "$_\n";
					} else {
						$is_create_log_changed = 1;
					}
					$create_count++; # カウントは別に行う
				}
			}
			if ($. < 1 || $is_create_log_changed) {
				seek($create_log_fh, 0, 0);
				truncate($create_log_fh, 0);
				print $create_log_fh $create_log;
			} else {
				seek($create_log_fh, 0, 2);
			}
			$is_recaptcha_enabled = $create_count + 1 > $recaptcha_thread_permit; # スレッド連続作成許可数を超えて書き込みをしようとしている、reCAPTCHA認証対象かどうか

			# 累積ログ ファイル・先頭行が存在しない場合は作成
			<$create_log_no_delete_fh>; # 先頭行読み飛ばし
			if ($. < 1) {
				seek($create_log_no_delete_fh, 0, 0);
				truncate($create_log_no_delete_fh, 0);
				print $create_log_no_delete_fh "日時,スレッドを作成したホスト（または登録ID）,タイムスタンプ\n";
			}
			seek($create_log_no_delete_fh, 0, 2);

			# reCAPTCHA認証対象ホストログ確認
			my $auth_host_log = "日時,スレッドタイトル,ホスト,タイムスタンプ\n";
			my $host_found_in_recaptcha_auth_log = 0;
			my $is_auth_host_log_changed = 0;
			<$auth_host_log_fh>; # 先頭行読み飛ばし
			while (<$auth_host_log_fh>) {
				chomp($_);
				my @line = split(/,/, $_);
				if (scalar(@line) == 4) {
					# 同一ホストが見つかった時、認証対象とする
					if ($line[2] eq $host) {
						$is_recaptcha_enabled = 1;
						$host_found_in_recaptcha_auth_log = 1;
					}
					# 自動消去が無効か、消去時間が経過していないログのみ残す
					if ($recaptcha_thread_auth_host_release_time == 0 || ($line[3] + $recaptcha_thread_auth_host_release_time >= $time)) {
						$auth_host_log .= "$_\n";
					} else {
						$is_auth_host_log_changed = 1;
					}
				}
			}
			# 消去ログでのみreCAPTCHA認証対象になったホストをログに追加
			if ($. < 1 || ($is_recaptcha_enabled && !$host_found_in_recaptcha_auth_log)) {
				$auth_host_log .= "$date,$i_sub,$host,$time\n";
				$is_auth_host_log_changed = 1;
			}
			if ($is_auth_host_log_changed) {
				seek($auth_host_log_fh, 0, 0);
				truncate($auth_host_log_fh, 0);
				print $auth_host_log_fh $auth_host_log;
			}
			close($auth_host_log_fh);

			$is_recaptcha_enabled ||= exists($in{'g-recaptcha-response'});
		} else {
			# ログファイルオープン失敗
			if ($create_log_fh) {
				close($create_log_fh);
			}
			if ($create_log_no_delete_fh) {
				close($create_log_no_delete_fh);
			}
			if ($auth_host_log_fh) {
				close($auth_host_log_fh);
			}
			error("Error: reCAPTCHA");
		}
	} else {
		# レス時reCAPTCHA認証が有効か、reCAPTCHAレスポンスが送信されてきた時に判定を実施する
		$is_recaptcha_enabled = ($in{'res'} ne '' && $recaptcha_res) || exists($in{'g-recaptcha-response'});
	}

	# 投稿キー・reCAPTCHA認証
	if ($is_recaptcha_enabled) {
		# reCAPTCHA認証
		# reCAPTCHAが表示されないか、チェックを行っていない時など
		# reCAPTCHAレスポンスが送信されてきていない時は、APIとの通信を行わない
		my $is_recaptcha_auth_success = 0;
		if ($in{'g-recaptcha-response'} ne '') {
			# reCAPTCHA APIと通信
			my $lwp_ua = LWP::UserAgent->new(timeout => 2);
			my $lwp_response = $lwp_ua->post(
				'https://www.google.com/recaptcha/api/siteverify',
				[ secret => $recaptcha_secret_key, response => $in{'g-recaptcha-response'} ]
			);

			if ($lwp_response->is_success) {
				# 正常に通信を行えた場合にのみ認証状況の確認を行う
				my $result = JSON::XS->new()->decode($lwp_response->content);
				if (${$result}{'success'} && Types::Serialiser::is_bool(${$result}{'success'})) {
					# 認証成功
					$is_recaptcha_auth_success = 1;
				}
			} else {
				# 通信失敗時は認証成功したものとみなす
				$is_recaptcha_auth_success = 1;
			}
		}

		# 認証失敗時はエラー表示
		if (!$is_recaptcha_auth_success) {
			if (exists($in{'regikey'}) || !exists($in{'g-recaptcha-response'})) {
				my $back_url;
				# 投稿キーが渡されたか、reCAPTCHAレスポンスフィールドがない場合
				if ($in{'res'} eq '') {
					# 新規スレッド作成のURLに戻る
					$back_url = "$readcgi?mode=form";
				} else {
					# スレッドのURLに戻る
					$back_url = "$readcgi?no=$in{'res'}" . ($in{'l'} ? "&l=$in{'l'}" : '');
				}
				error("前画面に戻り、ページを再読み込みして認証を行って下さい。", $back_url);
			} else {
				# reCAPTCHAが表示されているページだった場合は従来通りブラウザヒストリーで戻る
				error("認証に失敗しているか、有効期限が切れています。");
			}
		}
	} elsif (($in{'res'} eq '' && $regist_key_new) || ($in{'res'} ne '' && $regist_key_res)) {
		# 投稿キーチェック
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			error("投稿キーが入力不備です。<p>投稿フォームに戻って再読込み後、指定の数字を入力してください");
		}

		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
		local($chk) = &registkey_chk($in{'regikey'}, $in{'str_crypt'});
		if ($chk == 0) {
			error("投稿キーが制限時間を超過しました。<p>投稿フォームに戻って再読込み後、指定の数字を再入力してください");
		} elsif ($chk == -1) {
			error("投稿キーが不正です。<p>投稿フォームに戻って再読込み後、指定の数字を入力してください");
		}
	}

	# アクセス元IPアドレスが取得できている場合、VPNGate経由の書き込みであるかチェック
	if ($deny_post_via_vpngate && $addr =~ /^(?:(?:[1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:[1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])$/) {
		# VPNGate ボランティアVPNサーバIPアドレス存在確認用 HTTP APIと通信
		my $lwp_ua = LWP::UserAgent->new(timeout => 2);
		my $lwp_response = $lwp_ua->get("http://ipchecker.statistics.api.vpngate.net/api/ipcheck/?key=aepFZyCu&ip=${addr}");

		# 正常に通信を行えた場合にのみ
		# アクセス元IPアドレスがVPNGate ボランティアVPNサーバのものであるかどうかの返り値を確認し、
		# VPNGate経由の書き込みだった場合にエラーメッセージを表示
		if ($lwp_response->is_success && $lwp_response->content >= 1) {
			error("VPNGateからの書き込みはできません。");
		}
	}

	# WebProtect 登録ID連携認証
	if($webprotect_auth) {
		my $auth_result = WebProtectAuth::authenticate($in{'user_id'}, $in{'user_pwd'});
		if($auth_result == WebProtectAuth::ID_NOTFOUND) {
			&error($webprotect_auth_id_notfound_msg);
		} elsif($auth_result == WebProtectAuth::PASS_MISMATCH) {
			&error($webprotect_auth_pass_mismatch_msg);
		} elsif($auth_result != WebProtectAuth::SUCCESS) {
			&error("認証エラーが発生しました。管理者にご連絡下さい。");
		}
	}

	# トリップ
	$i_nam2 = &trip($i_nam);

	# パスワード暗号化
	my $pwd;
	if ($in{'pwd'} ne "") { $pwd = &encrypt($in{'pwd'}); }

	# スレッド更新日時管理データベース接続
	my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);

	# スレッドログ書き込み用書込ID
	my $threadlog_write_history_id = do {
		if (defined($chistory_id)) {
			if ($in{save_history}) {
				# 「書き込み履歴に記録する」チェック時
				"$chistory_id";
			} else {
				# 「書き込み履歴に記録する」未チェック時
				"$chistory_id@";
			}
		} else {
			# 書込IDが無いとき
			'';
		}
	};

	# 新規投稿（新規スレッド作成）
	if ($in{'res'} eq "") {

		# 管理者スレ立てチェック
		if ($createonlyadmin && $pass ne $in{'pwd'}) {
			&error("スレッドの作成は管理者のみに制限されています");
		}

		# 変数宣言
		local($i, $flg, $new_log, @tmp, $top_log, $faq_log);

		# index展開
		<$nowfile_fh>; # 先頭行読み飛ばし
		while(<$nowfile_fh>) {
#			local($sub,$key) = (split(/<>/))[1,6];
			chomp($_);
			local($no,$sub,$re,$nam,$d,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);

			$i++;
			# スレッド名重複
			my $checksub = $sub;
			$checksub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
			if ($checksub eq $in{'sub'}) {
				$flg++;
				last;
			} elsif ($key == 2) {
				$top_log .= "$_\n";
				next;
			} elsif ($key == 3) {
				$faq_log .= "$_\n";
				next;
			}

			# 規定数オーバーは@tmp代入
			if ($i >= $i_max) {
				push(@tmp,"$no<>$sub<>$re<>$nam<>$d<>$na2<>-1<>$upl<>$ressub<>$restime<>$host<>\n");

			# 規定数内は@new代入
			} else {
				$new_log .= "$_\n";
			}
		}

		# スレッド名重複はエラー
		if ($flg) {
			close($nowfile_fh);
			close($threadlog_fh);
			&error("<b>「$in{'sub'}」</b>は既存スレッドと重複しています。<br>別のスレッド名を指定してください");
		}

		# 現行index更新
		$new_log = "$new<>$i_sub<>0<>$i_nam2<>$date<>$i_nam2<>1<>$upl_flg<><>$time<>$host<>\n" . $new_log;
		$new_log = $faq_log . $new_log if ($faq_log);
		$new_log = $top_log . $new_log if ($top_log);
		$new_log = "$new<>$host<>$time<>\n" . $new_log;
		seek($nowfile_fh, 0, 0);
		print $nowfile_fh $new_log;
		truncate($nowfile_fh, tell($nowfile_fh));
		close($nowfile_fh);

		# 過去ログに落ちるスレッドのフラグを変更
		@tmp2 = @tmp;

		foreach my $tmp2 (@tmp2) {
			local($pastno) = split(/<>/, $tmp2);
			if ($pastno == '') { last; }

			# スレッド読み込み
			my $logfile_path = get_logfolder_path($pastno) . "/$pastno.cgi";
			open(my $pastlog_fh, '+<', $logfile_path) || &error("Open Error: $pastno.cgi");
			flock($pastlog_fh, 2) || error("Lock Error: $pastno.cgi");
			my $file = '';

			# 先頭行を抽出・分解し、フラグ変更・スレッド更新
			my $top = <$pastlog_fh>;
			my ($no,$sub,$res,undef) = split(/<>/, $top);
			$file .= "$no<>$sub<>$res<>-1<>\n";

			# スレッド残りの行を読み込み
			{
				local $/ = undef;
				$file .= <$pastlog_fh>;
			}

			seek($pastlog_fh, 0, 0);
			print $pastlog_fh $file;
			truncate($pastlog_fh, tell($pastlog_fh));
			close($pastlog_fh);

			# スレッド更新日時管理データベースで、過去ログに落ちたスレッド情報をアップデート
			$updatelog_db->update_threadinfo($pastno, undef, 0);
		}

		# 過去index更新
		if (@tmp > 0) {

			$j = @tmp;
			open(my $pastfile_fh, '+<', $pastfile) || &error("Open Error: $pastfile");
			flock($pastfile_fh, 2) || error("Lock Error: $pastfile_fh");
			while(<$pastfile_fh>) {
				$j++;
				if ($j > $p_max) {
					local($delno) = split(/<>/);

					# ログ展開
					my $logfile_path = get_logfolder_path($delno) . "/$delno.cgi";
					open(my $delthread_fh, $logfile_path);
					<$delthread_fh>;
					while (my $line = <$delthread_fh>) {
						$line =~ s/(?:\r\n|\r|\n)$//;

						my ($tim, %upl);
						($tim, $upl{1}, $upl{2}, $upl{3}, $upl{4}, $upl{5}, $upl{6}) = (split/<>/, $line)[11 .. 14, 23 .. 25];

						# 画像削除
						foreach $i (1 .. 6) {
							my ($img_folder_number, $ex) = split(/,/, $upl{$i});

							if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
								unlink("$upldir/$img_folder_number/$tim-$i$ex");
							}
							# サムネイル画像ファイルが存在したら削除
							if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
								unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
							}
						}
					}
					close($delthread_fh);

					unlink($logfile_path);

					# スレッド更新日時管理データベースから過去ログから削除されたスレッド情報を削除
					$updatelog_db->delete_threadinfo($delno);

					next;
				}
				push(@tmp,$_);
			}
			seek($pastfile_fh, 0, 0);
			print $pastfile_fh @tmp;
			truncate($pastfile_fh, tell($pastfile_fh));
			close($pastfile_fh);
		}

		# スレッド更新
		my $logfolder_path = get_logfolder_path($new);
		my $logfile_path = "$logfolder_path/$new.cgi";
		if (!-e $logfolder_path) { # 保存フォルダがない場合は新規作成
			mkdir($logfolder_path);
			chmod(0777, $logfolder_path);
		}
		open($log_fh, '+>', $logfile_path) || &error("Write Error: $new.cgi");
		print $log_fh "$new<>$i_sub<>$newno<>1<>\n";
		print $log_fh join('<>',
			'1',
			$in{'sub'},
			$i_nam2,
			$in{'email'},
			$i_com,
			$date,
			$host,
			$pwd,
			$in{'url'},
			$in{'mvw'},
			$my_id,
			$time,
			"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
			"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
			"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
			$idcrypt,
			$in{'user_id'},
			'', # スレッド作成時なので、sageフラッグは常にfalse
			$cookie_a->value(),
			$threadlog_write_history_id,
			$useragent,
			$is_private_browsing_mode,
			$first_cookie->get_first_access_datetime(),
			"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
			"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
			"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
			"\n"
		);
		close($log_fh);

		# パーミッション変更
		chmod(0666, $logfile_path);

		# スレッド更新日時管理データベースに作成したスレッド情報を記録
		$updatelog_db->create_threadinfo($new, $time, 1);

		# 日付別スレッド作成数ログファイル 作成数カウントアップ
		&regist_log_countup($thread_create_countlog);

		# 新規投稿記録ファイルに追記
		$add_to_threadlog->();

		&sendmail if ($mailing);

	# 返信投稿
	} else {

		# 連続投稿チェック
#		local($top);
#		open(IN,"$nowfile") || &error("Open Error: $nowfile");
#		$top = <IN>;
#		close(IN);
#
#		local($no,$hos2,$tim2) = split(/<>/, $top);
#		if ($host eq $hos2 && $wait_response > time - $tim2) {
#			&error("連続投稿はもうしばらく時間をおいて下さい");
#		}

		# 先頭ファイルを抽出・分解
		local ($no, $thread_title, $res, $key) = @{$log[0]};

		# スレッドタイトルによる投稿間隔の変更機能
		# 投稿間隔・ログファイルの決定
		my $wait_response = $wait_response_default;
		my $responselog = $responselog_default;
		if (defined($mu->universal_match([$thread_title], [$wait_response_word1], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response1;
			$responselog = $responselog1;
		} elsif (defined($mu->universal_match([$thread_title], [$wait_response_word2], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response2;
			$responselog = $responselog2;
		} elsif (defined($mu->universal_match([$thread_title], [$wait_response_word3], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response3;
			$responselog = $responselog3;
		}

		# 連続投稿IP/登録IDチェック・レス投稿ログへの記録内容を作成(まだ書き込みは行わない)
		my $reslog_contents = "$postLimitComparisonFirstItem<>$time<>$user_id_is_post_limit_comparision_item<>\n";
		open(my $reslog_fh, '+<', $responselog) || &error("Open Error: $responselog");
		flock($reslog_fh, 2) || &error("Lock Error: $responselog");
		seek($reslog_fh, 0, 0);
		{
			my $record_count = 1; # ログ件数
			while(<$reslog_fh>) {
				chomp($_);
				if ($_ eq '') {
					next;
				}
				my ($record_user_id_or_host, $post_time, $record_first_item_type) = split(/<>/);
				# 制限時間内かどうか判定
				if ($post_time + $wait_response > $time) {
					# 同一ユーザーかどうか判定
					if ($record_first_item_type == $user_id_is_post_limit_comparision_item && $record_user_id_or_host eq $postLimitComparisonFirstItem) {
						close($reslog_fh);
						&error("連続投稿はもうしばらく時間をおいて下さい");
					} elsif ($record_count < $hostnum) {
						# 制限時間内の他ユーザーのログを記録内容に追加
						$reslog_contents .= "$_\n";
						$record_count++;
					}
				}
			}
		}

		# ロックチェック
		if ($key eq '0' || $key eq '2') {
			close($log_fh);
			&error("このスレッドはロック中のため返信できません");
		}

		# 過去ログチェック
		if ($key eq '-1') {
			close($log_fh);
			&error("過去ログのスレッドには返信できません");
		}

		# 重複投稿判定
		my ($lastres_com, $lastres_host, $lastres_user_id, $lastres_cookie_a, $lastres_history_id) = @{$log[$#log]}[4, 6, 16, 18, 19];
		$lastres_history_id =~ s/\@$//; # 書込ID末尾に@がある場合は取り除く
		if (is_duplicate_post(
			$thread_title,
			$upl_flg, $i_com, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $host,
			$lastres_com, $lastres_cookie_a, $lastres_user_id, $lastres_history_id, $lastres_host,
			\@duplicate_post_restrict_thread
		)) {
			error("重複投稿は禁止です");
		}

		# NGスレッド機能 スレッド作成者の名前上書き
		my $is_ngthread_name_override = $newno <= $ngthread_thread_list_creator_name_override_max_res_no && ngthread_name_override_judge($i_nam2, $in{'user_id'}, $cookie_a, $chistory_id, $log[1]);

        # ホストなどによるageの無効
        if ($mu->is_disable_age($check_i_sub, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode, \@disable_age)) {
            # 設定に合致する場合は強制的にsage投稿とする
            $in{'sage'} = '1';
        }

		# 記事数チェック
		if ($m_max < $newno) { &error("最大記事数をオーバーしたため投稿できません"); }
		elsif ($m_max == $newno) { $maxflag = 1; }
		else { $maxflag = 0; }

		# IDを作成
		if($idkey) { &makeid; }
		else { $idcrypt = "";}

		# スレッド更新
#		$res++;
#		unshift(@file,"$no<>$sub<>$res<>$key<>\n");
		$file = "$no<>$i_sub<>$newno<>$key<>\n" . $file;
		$file .= join('<>',
			$newno,
			$in{'sub'},
			$i_nam2,
			$in{'email'},
			$i_com,
			$date,
			$host,
			$pwd,
			$in{'url'},
			$in{'mvw'},
			$my_id,
			$time,
			"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
			"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
			"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
			$idcrypt,
			$in{'user_id'},
			$in{'sage'},
			$cookie_a->value(),
			$threadlog_write_history_id,
			$useragent,
			$is_private_browsing_mode,
			$first_cookie->get_first_access_datetime(),
			"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
			"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
			"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
			"\n"
		);

		seek($log_fh, 0, 0);
		print $log_fh $file;
		truncate($log_fh, tell($log_fh));
		close($log_fh);

		## 規定記事数オーバのとき ##
		if ($maxflag) {

			# 過去ログindex読み込み
			open(my $pastfile_fh, '+<', $pastfile) || &error("Open Error: $pastfile");
			flock($pastfile_fh, 2) || &error("Lock Error: $pastfile");
			my $file;
			{
				local $/ = undef;
				$file = <$pastfile_fh>;
			}

			# 現行ログindexから該当スレッド抜き出し
			local($top, $new_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$d,$na2,$key,$upl,undef,undef,$host) = split(/<>/);

				if ($in{'res'} == $no) {
					$re++;
					if ($is_ngthread_name_override) {
						# NGスレッド機能 スレッド作成者の名前上書き
						# スレッド作成者名を投稿者名で上書きする
						$nam = $i_nam2;
					}
					$file = "$no<>$sub<>$newno<>$nam<>$date<>$na2<>-1<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $file;
					next;
				}
				$new_log .= "$_\n";
			}

			# 現行ログindex更新
			$new_log = $top . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);

			# 過去ログindex更新
			seek($pastfile_fh, 0, 0);
			print $pastfile_fh $file;
			truncate($pastfile_fh, tell($pastfile_fh));
			close($pastfile_fh);

		## ソートあり (age) ##
		} elsif ($in{'sage'} ne '1') {

			# indexファイル更新
			local($flg, $top, $new_log, $top_log, $faq_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$da,$na2,$key,$upl,undef,undef,$host) = split(/<>/);

				if ($key == 2) {
					$top_log .= "$_\n";
					next;
				}
				if ($key == 3 && $in{'res'} != $no) {
					$faq_log .= "$_\n";
					next;
				}
				if ($key == 3 && $in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NGスレッド機能 スレッド作成者の名前上書き
						# スレッド作成者名を投稿者名で上書きする
						$nam = $i_nam2;
					}
					$faq_log = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $faq_log;
					next;
				} elsif ($in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NGスレッド機能 スレッド作成者の名前上書き
						# スレッド作成者名を投稿者名で上書きする
						$nam = $i_nam2;
					}
					$new_log = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $new_log;
					next;
				}
				$new_log .= "$_\n";
			}

			if (!$flg) {
				&error("該当のスレッドがindexファイルに見当たりません");
			}

			local($no2,$host2,$time2) = split(/<>/, $top);

#			unshift(@new,$new);
			$new_log = $faq_log . $new_log if ($faq_log);
			$new_log = $top_log . $new_log if ($top_log);
			$new_log = "$no2<>$host<>$time<>\n" . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);

		## ソートなし (sage) ##
		} else {

			# indexファイル更新
			local($flg, $top, $new_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$da,$na2,$key,$upl,undef,undef,$host) = split(/<>/);
				if ($in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NGスレッド機能 スレッド作成者の名前上書き
						# スレッド作成者名を投稿者名で上書きする
						$nam = $i_nam2;
					}
					$_ = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>";
				}
				$new_log .= "$_\n";
			}

			if (!$flg) {
				&error("該当のスレッドがindexファイルに見当たりません");
			}

			local($no2,$host2,$time2) = split(/<>/, $top);

			$new_log = "$no2<>$host<>$time<>\n" . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);
		}

		# FAQカウント
#		&faqcount ($i_com,$in{'res'});

		# スレッド更新日時管理データベースで、スレッド情報をアップデート
		$updatelog_db->update_threadinfo($in{'res'}, $time, !$maxflag ? 1 : 0);

		# 日付別レス書き込み数ログファイル 書き込み数カウントアップ
		&regist_log_countup($response_countlog);

		# レス投稿ログへ記録
		seek($reslog_fh, 0, 0);
		print $reslog_fh $reslog_contents;
		truncate($reslog_fh, tell($reslog_fh));
		close($reslog_fh);

		# メール送信
		&sendmail if ($mailing == 2);

		# レスお知らせメール送信
		&sendnotify if ($mailnotify != 0);
	}

	# スレッド更新日時管理データベース切断
	$updatelog_db->close(0);

	# 登録ID認証成功ログへ記録
	if($webprotect_auth && $webprotect_authlog) {
		local $/ = undef;
		my $tmp = "$in{'user_id'}<>$date\n";
		open(my $webprotect_authlog_fh, '+<', $webprotect_authlog_path) || &error("Open Error: $webprotect_authlog_path");
		flock($webprotect_authlog_fh, 2) || &error("Open Error: $webprotect_authlog_path");
		$tmp .= <$webprotect_authlog_fh>;
		seek($webprotect_authlog_fh, 0, 0);
		print $webprotect_authlog_fh $tmp;
		truncate($webprotect_authlog_fh, tell($webprotect_authlog_fh));
		close($webprotect_authlog_fh);
	}

	# reCAPTCHA認証 消去ログ/累積ログ追記
	if ($in{'res'} eq '' && ($recaptcha_thread || $is_recaptcha_enabled)) {
		my $host_or_user_id = $webprotect_auth ? $in{'user_id'} : $host;
		my $recaptcha_thread_create_log_append_contents = "$date,$host_or_user_id,$time\n";
		if ($create_log_fh) {
			if ($recaptcha_thread_create_log_append_contents ne '') {
				print $create_log_fh $recaptcha_thread_create_log_append_contents;
			}
			close($create_log_fh);
		}
		if ($create_log_no_delete_fh) {
			if ($recaptcha_thread_create_log_append_contents ne '') {
				print $create_log_no_delete_fh $recaptcha_thread_create_log_append_contents;
			}
			close($create_log_no_delete_fh);
		}
	}

	# 書き込みログ出力機能
	if ($post_log) {
		my $post_log_filepath = do {
			my $log_dir = File::Spec->canonpath($post_log_dir); # 出力ディレクトリパス正規化
			my $date = strftime('%Y%m%d', @localtime); # 日付フォーマット
			File::Spec->catfile($log_dir, $date . $post_log_filename_suffix); # 出力ファイルパスを作成
		};
		my $post_log_fh;
		if (open($post_log_fh, '>>', $post_log_filepath) && flock($post_log_fh, 2)) { # ファイルを正常にオープン・ロックできた場合のみ書込みする
			# ファイルが空の場合には、ヘッダー行を追加
			if (-s $post_log_filepath == 0) {
				# ヘッダー定義
				my @header = (
					'日時',
					'$bbs_pass',
					'スレッド番号',
					'スレッド名',
					'カテゴリ',
					'スレ作成orレス',
					'レス番号',
					'名前',
					'age、sage',
					'ユーザーID',
					'プライベートモード',
					'初回アクセス時間',
					'CookieA発行',
					'ユニークCookieA',
					'登録ID',
					'書込ID',
					'ホスト',
					'文字数',
					'レス内容'
				);
				foreach my $i (1 .. 6) {
					push(@header,
						"画像$i",
						"画像${i}のMD5（変換前）",
						"画像${i}のMD5（変換後）"
					);
				}
				push(@header, 'UserAgent');

				# ヘッダー出力
				print $post_log_fh join(',', @header) . "\n";
			}

			# 書き込み項目セット
			my $thread_no = $in{'res'} eq '' ? $new : $in{'res'};         # スレッド番号
			(my $sub = $i_sub) =~ tr/,//d;                                # カンマを除いたスレッド名
			my $category = do {                                           # カテゴリ
				my $tmp_category = '-';
				my $tmp_sub = $enc_cp932->decode($sub); # スレッド名を一致判定のため内部文字列へ変換
				foreach my $conv_set (@category_convert) {
					my $decoded_conv_set = $enc_cp932->decode($conv_set); # 変換セットを一致判定のため内部文字列へ変換
					my ($keyword, $cat) = split(/:/, $decoded_conv_set, 2);
					if ($keyword eq '') {
						next; # カテゴリキーワードが空の時はスキップ
					}
					my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
					if ($tmp_sub =~ /$capture_regex/) {
						# 対応するカテゴリ名を設定
						$tmp_category = $enc_cp932->encode($cat);
						# スレッド名からカテゴリキーワードを除いて再セット
						$tmp_sub = $1;
						$sub = $enc_cp932->encode($tmp_sub);
						last;
					}
				}
				$tmp_category;
			};
			my $formatted_date = do { # 日付
				my ($sec, $min, $hour, $mday, $mon, $year) = @localtime[0..5];
				sprintf("%s/%02d/%02d %02d:%02d:%02d", substr($year+1900, -2), $mon+1, $mday, $hour, $min, $sec);
			};
			my $post_type = $in{'res'} eq '' ? 'スレ作成' : 'レス';       # スレ作成 or レス
			my $res_no = $in{'res'} eq '' ? 1 : $newno;                   # レス番号
			(my $nam = $i_nam2) =~ tr/,//d;                               # カンマを除いた名前
			my $sage = $in{'res'} ne '' ? ($in{'sage'} eq '1' ? 'sage' : 'age') : '-'; # age / sage
			my $idcrypt = $idcrypt ne '' ? $idcrypt : '-';                # ユーザーID
			my $private_browsing_mode = $is_private_browsing_mode ? '有効' : '-'; # プライベートブラウジングモード
			my $first_access_time = $first_cookie->value(1) || '-'; # 初回アクセス時間
			my $issuing_cookie_a = $is_cookie_a_issuing ? '発行' : '-';   # CookieAを発行したかどうか
			my $post_log_cookie_a = $cookie_a->value() ne '' ? $cookie_a->value() : '-'; # ユニークCookieA
			my $user_id = exists($in{'user_id'}) ? $in{'user_id'} : '-';  # 登録ID
			my $history_id = $chistory_id ne '' ? $chistory_id : '-';      # 書込ID
			# レス内容の文字数を取得
			my $res_length = do {
				my $normalized_res = $enc_cp932->decode($i_com);
				$normalized_res =~ s/<br>//g;
				$normalized_res = HTML::Entities::decode($normalized_res);
				length($normalized_res);
			};
			(my $com = $i_com) =~ tr/,//d;                                # カンマを除いたレス内容を取得
			$com = replace_contents_for_post_log($com);                   # レス内容を「書き込みログの置換記録機能」の設定値に応じて置換
			if ($com eq '') { $com = '-'; }                               # レス内容が空の場合に「-」をセット
			my @imgs; # 画像1～6, 画像1～6のMD5(変換前), 画像1～6のMD5(変換後)を格納する配列
			foreach my $i (1 .. 6) {
				my $img = $ex{$i} ne '' ? "$fn{$i}/$time-$i$ex{$i}" : '-'; # 画像1～6
				my $img_orig_md5 = $image_orig_md5{$i} ne '' ? $image_orig_md5{$i} : '-'; # 画像1～6のMD5（変換前)
				my $img_conv_md5 = $image_conv_md5{$i} ne '' ? $image_conv_md5{$i} : '-'; # 画像1～6のMD5（変換後)
				push(@imgs, $img, $img_orig_md5, $img_conv_md5);
			}
			my $useragent = $useragent ne '' ? $useragent : '-';          # UserAgent

			# 書き込みログに追記
			print $post_log_fh join(',',
				$formatted_date, # 日時
				$bbs_pass, # $bbs_pass
				$thread_no, # スレッド番号
				$sub, # スレッド名
				$category, # カテゴリ
				$post_type, # スレ作成orレス
				$res_no, # レス番号
				$nam, # 名前
				$sage, # age、sage
				$idcrypt, # ユーザーID
				$private_browsing_mode, # プライベートモード
				$first_access_time, # 初回アクセス時間
				$issuing_cookie_a, # CookieA発行
				$post_log_cookie_a, # ユニークCookieA
				$user_id, # 登録ID
				$history_id, # 書込ID
				$host, # ホスト
				$res_length, # 文字数
				$com, # レス内容
				@imgs, # 画像1～6, 画像1～6のMD5(変換前), 画像1～6のMD5(変換後)
				$useragent # UserAgent
			) . "\n";
		}
		close($post_log_fh);
	}

	# クッキーを格納
	if ($in{'cook'} eq 'on') {
		# Cookie取得
		my @cookie = get_cookie();

		# 「スレッドをトップへソート」/「sage」 Cookie取得
		my ($cthread_sort, $thread_sage) = @cookie[7,8];

		# 返信投稿時のみ、フォームからの「sage」チェック状態で上書き
		if($in{'res'} ne '') {
			$thread_sage = $in{'sage'} eq '1' ? '1' : '0';
		}

		# WebProtect 登録ID
		my ($user_id, $user_pwd) = do {
			if (($in{'res'} eq '' && $webprotect_auth_new) || ($in{'res'} ne '' && $webprotect_auth_res)) {
				# 登録ID認証が有効の場合、フォーム入力値を使用
				($in{'user_id'}, $in{'user_pwd'});
			} else {
				# 登録ID認証が無効の場合、既にCookieにセットされている値を使用
				@cookie[5,6];
			}
		};

		# 書き込み履歴に記録する フラグ
		my $save_history = $cookie[9];
		if (exists($in{save_history})) {
			# フォームからチェックボックスの状態が送信されてきた場合のみ、
			# Cookieに上書き記録する
			$save_history = int($in{save_history}) ? 1 : 0;
		}

		# 名前欄
		my $name = $is_hide_name_field_in_form ? $cookie[0] : $i_nam; # 名前欄非表示機能適用時は、Cookieの値を引き継ぐ

		# 3枚以上アップロードする チェックフラグ
		my $increase_upload_num_checked = $cookie[10];
		if (exists($in{'increase_num'})) {
			$increase_upload_num_checked = $in{'increase_num'} eq '1';
		}

		# Cookie セット
		&set_cookie($name, $in{email}, $in{pwd}, $in{url}, $in{mvw}, $user_id, $user_pwd, $cthread_sort, $thread_sage, $save_history,
			$increase_upload_num_checked);
	}

	# 書き込み履歴ログに記録
	my $decoded_check_i_sub = $enc_cp932->decode($check_i_sub);
	if ($in{save_history} && defined($chistory_id) && $chistory_id ne ''
		&& scalar(grep { $_ ne '' && index($decoded_check_i_sub, $_) != -1 } @history_save_exempt_titles) == 0) {
		# 書き込みスレッド情報を決定
		my $thread_no = int($in{'res'} eq '' ? $new : $in{'res'}); # スレッド番号
		my $res_no = int($in{'res'} eq '' ? 1 : $newno);           # 投稿レスNo.
		# 書き込み履歴ログに記録
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->add_post_history($thread_no, $res_no, int($time));
		$history_log->DESTROY();
	}

	# 完了メッセージ
	&header;
	$md = 'view';
	if ($in{'res'} eq "") { $no = $new; }
	else { $no = $in{'res'}; }

	print <<EOM;
<br><br><div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="400">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center" height="60">
	<h3 style="font-size:15px">ご投稿ありがとうございました</h3>
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
EOM

	# 過去ログ繰り越しの場合
	if ($maxflag) {
		print "ただし１スレッド当りの最大記事数を超えたため、<br>\n";
		print "このスレッドは <a href=\"$readcgi?mode=past\">過去ログ</a> ";
		print "へ移動しました。\n";
		$md = 'past';
	}

	# 戻りフォーム
	print <<"EOM";
<table><tr><td valign="top">
<form action="$bbscgi">
<input type="submit" value="掲示板へ戻る">
</form></td><td width="15"></td>
<td valign="top">
<form action="$readcgi" method="post">
<input type="hidden" name="mode" value="$md">
<input type="hidden" name="no" value="$no">
<input type="submit" value="スレッドを見る">
</form></td>
</tr>
</table>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  記事削除（使ってないようなので削除）
#-------------------------------------------------
# sub delete {}


#-------------------------------------------------
#  メンテ処理
#-------------------------------------------------
sub mente {
	# 汚染チェック
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# 記事修正
	if ($in{'job'} eq "edit") {
		if ($in{'pwd'} eq '') { &error("パスワードの入力モレです"); }

		require $editlog;
		&edit_log("user");

	# 削除処理
	} elsif ($in{'job'} eq "del") {

		if ($in{'pwd'} eq '') { &error("パスワードの入力モレです"); }

		# スレッドより削除記事抽出
		my ($flg, $top, $check, $new_log, $last_tim, $last_nam, $last_dat, $last_sub);
		my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		my $res = (split(/<>/, $top))[2]; # ログに記録するレス数を取得
#		$j=-1;
		my $res_cnt = 0; # 最終レス情報決定用レス数カウンタ (ログに記録するレス数は$resをそのまま使用)
		while(<DAT>) {
			local($no,$sub,$nam,$eml,$com,$dat,$ho,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl{4},$upl{5},$upl{6}) = split(/<>/);

			# スレッド内で一番最後に更新された記事の時刻を覚える
#			if ($tim ne 0 && $tim > $lrtime) { $lrtime = $tim; }

			if ($in{'no'} == $no) {
				$flg = 1;

				# 管理パスワードで削除
				if ($in{'pwd'} ne $pass) {
					# パス照合
					$check = &decrypt($in{'pwd'}, $pw);
				}

				# スレッドヘッダのレス個数を調整
#				($num,$sub2,$res,$key) = split(/<>/, $top);
#				$res--;
#				$top = "$num<>$sub2<>$res<>$key<>\n";

				# 添付削除
				foreach my $i (1 .. 6) {
					my ($img_folder_number, $ex) = split(/,/, $upl{$i});

					if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
						unlink("$upldir/$img_folder_number/$tim-$i$ex");
					}
					# サムネイル画像ファイルが存在したら削除
					if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
						unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
					}
				}

				# 削除したならスキップ
#				$j++;
				next;
			}
			$new_log .= $_;
			$res_cnt++;

			# スレッド内で一番最後に更新された記事の時刻を覚える
			if ($tim ne 0 && $tim > $last_tim) { $last_tim = $tim; }

			# 最終記事の投稿者と時間を覚えておく
			$last_nam = $nam;
			$last_dat = $dat;
			# タイトルも
			$last_sub = $sub;
		}

		if (!$flg) { &error("該当記事が見当たりません"); }
#		if (!$check) { &error("パスワードが違います"); }
		if (!$check && $in{'pwd'} ne $pass ) { &error("パスワードが違います"); }

		$res_cnt--; # レスカウントから親レスを除く
		if ($res_cnt == 0) {
			# 最終的にレスがない場合
#			$last_nam = "";
#			$last_dat = "";
			$last_sub = "";
#			$last_tim = "";
		}

		# スレッド更新
		$new_log = $top . $new_log;
		seek(DAT, 0, 0);
		print DAT $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# index展開
		my ($top_log, $faq_log, @new, @sort) = ('', '');
#		local($top, @sort, @top, @faq);
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			chomp($_);
			local($no,$sub,$re,$nam,$dat,$na2,$key,$upl) = split(/<>/);

			if ($key == 2) {
				$top_log .= "$_\n";
				next;
			}
			if ($key == 3 && $in{'f'} != $no) {
				$faq_log .= "$_\n";
				next;
			}
			if ($key == 3 && $in{'f'} == $no) {
				# indexのレス個数を調整し、最終投稿者と時間を置換
#				$res--;
#				$na2 = $last_nam;
#				$dat = $last_dat;
# レスがない場合は、レスのタイトルを空欄に
#				if ($j < 1) {$last_sub="";}
				$faq_log .= "$no<>$sub<>$res<>$nam<>$dat<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>\n";
				next;
			}
			if ($in{'f'} == $no) {
				# indexのレス個数を調整し、最終投稿者と時間を置換
#				$res--;
#				$na2 = $last_nam;
#				$dat = $last_dat;
# レスがない場合は、レスのタイトルを空欄に
#				if ($j < 1) {$last_sub="";}
				$_ = "$no<>$sub<>$res<>$nam<>$dat<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>";
			}
			push(@new,"$_\n");

			# ソート用配列
			$dat =~ s/\D//g;
			push(@sort,$dat);
		}

		# 投稿順にソート
		@new = @new[sort {$sort[$b] <=> $sort[$a]} 0..$#sort];

		# index更新
		unshift(@new,$faq_log) if ($faq_log);
		unshift(@new,$top_log) if ($top_log);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

		# スレッド更新日時管理データベースで、レス削除後のスレッド情報にアップデート
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($in{'f'}, $last_tim, undef);
		$updatelog_db->close(0);

		# 完了メッセージ
		&header;
		print "<div align=\"center\">\n";
		print "<b>記事は正常に削除されました。</b>\n";
		print "<form action=\"$bbscgi\">\n";
		print "<input type=\"submit\" value=\"掲示板へ戻る\"></form>\n";
		print "</div></body></html>\n";
		exit;

	# ロック処理
	} elsif ($in{'job'} eq "lock") {

		if ($in{'pwd'} eq '') { &error("パスワードの入力モレです"); }

		my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";

		# スレッド一部読み込み
		my $top = <DAT>;
		my $parent_res = <DAT>;

		# パスワードチェック
		local($no,$sb,$na,$em,$com,$da,$ho,$pw) = split(/<>/, $parent_res);

# 管理者ロック
		if ($in{'pwd'} eq $pass) {}
		elsif (!&decrypt($in{'pwd'}, $pw)) { &error("パスワードが違います"); }

		# スレッド残り読み込み
		my $file;
		{
			local $/ = undef;
			$file = <DAT>;
		}

		# 更新
		local($num,$sub,$res,$key) = split(/<>/, $top);
		if ($in{'pwd'} eq $pass && $key == 4) { $key = 1;}
		elsif ($in{'pwd'} eq $pass ) { $key = 4; }
		elsif ($in{'pwd'} ne $pass && $key == 4) { &error("管理者ロックされています"); }
		elsif ($key == 1) { $key = 0; }
		elsif ($key == 0) { $key = 1; }
		$top = "$num<>$sub<>$res<>$key<>\n";

		seek(DAT, 0, 0);
		print DAT $top . $parent_res . $file;
		truncate(DAT, tell(DAT));
		close(DAT);

		# index展開
		my $new_log;
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			chomp($_);
			local($no,$sub,$res,$nam,$da,$na2,$key2,$upl,$ressub,$restime) = split(/<>/);

			if ($in{'f'} == $no) {
				$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>";
			}
			$new_log .= "$_\n";
		}

		# index更新
		$new_log = $top . $new_log;
		seek(DAT, 0, 0);
		print DAT $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 完了メッセージ
		&header;
		print "<div align=\"center\">\n";

		if ($key == 4) {
			print "<b>スレッドは管理者によりロックされました。</b>\n";
		} elsif ($key == 1) {
			print "<b>スレッドはロック解除されました。</b>\n";
		} else {
			print "<b>スレッドはロックされました。</b>\n";
		}

		print "<form action=\"$bbscgi\">\n";
		print "<input type=\"submit\" value=\"掲示板へ戻る\"></form>\n";
		print "</div></body></html>\n";
		exit;
	}

	# 該当ログチェック
	$flg = 0;
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(IN, $logfile_path);
	$top = <IN>;
	while (<IN>) {
		($no,$sub,$name,$email,$com,$date,$host,$pw) = split(/<>/);

		if ($in{'no'} == $no) {
			$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
			last;
		}
	}
	close(IN);

	# 管理者による変更ができるように無効化
#	if ($pw eq "") {
#		&error("該当記事はパスワードが設定されていません");
#	}

	($num,$sub2,$res,$key) = split(/<>/, $top);

	&header;
	print <<"EOM";
<div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/mente.gif" align="top">
&nbsp; <b>メンテフォーム</b></td>
<td align="right" bgcolor="$col3" nowrap>
<a href="javascript:history.back()">前画面に戻る</a></td>
</tr></table></Td></Tr></Table>
<P>
<form action="$registcgi" method="post">
<input type="hidden" name="mode" value="mente">
<input type="hidden" name="f" value="$in{'f'}">
<input type="hidden" name="no" value="$in{'no'}">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>対象スレッド</td>
  <td>件名： <b>$sub</b><br>名前： <b>$name</b>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>処理選択</td>
  <td><select name="job">
	<option value="edit" selected>記事を修正
EOM

	if ($in{'no'} eq "") {
		if ($key == 1) {
			print "<option value=\"lock\">スレッドをロック\n";
		} elsif ($key == 0) {
			print "<option value=\"lock\">ロックを解除\n";
		}
	} else {
		print "<option value=\"del\">記事を削除\n";
	}

	print <<"EOM";
	</select>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>パスワード</td>
  <td><input type="password" name="pwd" size="10" maxlength="8">
	<input type="submit" value="送信する">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM

	print <<"EOM";
<P>
<form action="$admincgi" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="logfile" value="1">
<input type="hidden" name="no" value="$in{'f'}">
EOM

	if ($in{'no'} eq "") {
	print <<"EOM";
<input type="hidden" name="no2" value="0">
EOM
	} else {
	print <<"EOM";
<input type="hidden" name="no2" value="$in{'no'}">
EOM
	}

	print <<"EOM";
<input type="hidden" name="action" value="view">
<input type="hidden" name="job" value="split">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>管理者モード</td>
  <td>このレスでスレッド分割
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>管理パスワード</td>
  <td><input type="password" name="pass" size="10" maxlength="8">
	<input type="submit" value="スレッド分割（管理者のみ）">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM

	if ($in{'no'} eq "") {
	print <<"EOM";
<P>
<form action="$admincgi" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="logfile" value="1">
<input type="hidden" name="action" value="del">
<input type="hidden" name="no" value="$in{'f'}">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>管理者モード</td>
  <td>スレッド削除
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>管理パスワード</td>
  <td><input type="password" name="pass" size="10" maxlength="8">
	<input type="submit" value="スレッド削除（管理者のみ）">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM
	}

	print <<"EOM";
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  クッキー発行
#-------------------------------------------------
sub set_cookie {
	local(@cook) = @_;
	local($gmt, $cook, @t, @m, @w);

	@t = gmtime(time + 60*24*60*60);
	@m = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
	@w = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');

	# 国際標準時を定義
	$gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
			$w[$t[6]], $t[3], $m[$t[4]], $t[5]+1900, $t[2], $t[1], $t[0]);

	# 保存データをURLエンコード
	foreach (@cook) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	# 格納
	my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}";
	print "Set-Cookie: $cookie_name=$cook; expires=$gmt\n";
}

#-------------------------------------------------
#  メール送信
#-------------------------------------------------
sub sendmail {
	local($msub, $mbody, $mcom, $email);

	# メールタイトルを定義
	$msub = "$title： $i_sub";

	# 本文の改行・タグを復元
	$mcom = $i_com;
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/＜/g;
	$mcom =~ s/&gt;/＞/g;
	$mcom =~ s/&quot;/”/g;
	$mcom =~ s/&amp;/＆/g;

$mbody = <<EOM;
--------------------------------------------------------
$titleに以下の投稿がありましたのでお知らせします。
これはシステムからの自動送信メールです。
迷惑投稿の場合は申\し訳ありませんが無視してください。
じきに削除します。

投稿日時：$date
ホスト名：$host
ブラウザ：$ENV{'HTTP_USER_AGENT'}

おなまえ：$i_nam2
Ｅメール：$in{'email'}
タイトル：$i_sub
ＵＲＬ  ：$in{'url'}

$mcom

スレッドを見る
$fullscript?&no=$no
--------------------------------------------------------
EOM

	# 題名をBASE64化
	$msub = &base64($msub);

	# メールアドレスがない場合は管理者アドレスに置き換え
	if ($in{'email'} eq "") { $email = $mailto; }
	else { $email = $in{'email'}; }

	# sendmail送信
	open(MAIL,"| $sendmail -t -i") || &error("送信失敗");
	print MAIL "To: $mailto\n";
	print MAIL "From: $email\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $ver\n\n";
	foreach ( split(/\n/, $mbody) ) {
		&jcode'convert(*_, 'jis', 'sjis');
		print MAIL $_, "\n";
	}
	close(MAIL);
}

#-------------------------------------------------
#  レスお知らせ送信
#-------------------------------------------------
sub sendnotify {
	local($msub,$mbody,$mcom,$email,$no,$sub,@maillist,$eml,$top,$top2,$flg,@maillist2);

	# スレッド解体
	# スレッド読み込み
	my $logfile_path = get_logfolder_path($in{'res'}) . "/$in{'res'}.cgi";
	open(IN, $logfile_path) || &error("Open Error: $in{'res'}.cgi");
	@file = <IN>;
	close(IN);

	# 先頭ファイルを抽出、分解
	$top = shift(@file);
	($no,$sub,undef,undef) = split(/<>/, $top);
	$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

	# メールアドレスを抽出
	# トップ記事
	$top2 = shift(@file);
	(undef,undef,undef,$eml,undef,undef,undef,undef,undef,undef,undef,undef,undef) = split(/<>/, $top2);
	if ($eml ne "") {
		foreach ( split(/,/, $refuseaddr) ) {
			if (index("$eml",$_) >= 0) {
				$flg = 1; last;
			}
		}
		if ($flg == 0){
			push(@maillist,$eml);
		}
	}

	# レス記事
	if ($mailnotify==2 && $#file >= 0) {

		foreach ( @file ){
		# print $value, "\n";
			(undef,undef,undef,$eml,undef,undef,undef,undef,undef,undef,undef,undef,undef) = split(/<>/);
			if ($eml ne "") {
				$flg = 0;
				foreach ( split(/,/, $refuseaddr) ) {
					if (index("$eml",$_) >= 0) {
						$flg = 1; last;
					}
				}
				if ($flg == 0){
					push(@maillist,$eml);
				}
			}
		}
	}

	# メールアドレスの重複の削除
	my %uniq = map {$_ => 1} @maillist;
	my @maillist2 = keys %uniq;

#	my %count;
#	@maillist = grep {!$count{$_}++} @maillist;

#	print "@maillist";

	# メールタイトルを定義
	$msub = "$title： [$no] $sub";

	# 本文の改行・タグを復元
	$mcom = $i_com;
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/＜/g;
	$mcom =~ s/&gt;/＞/g;
	$mcom =~ s/&quot;/”/g;
	$mcom =~ s/&amp;/＆/g;

$mbody = <<EOM;
--------------------------------------------------------
$titleの
「[$no] $sub」に新しいレスがありましたのでお知らせします。

タイトル：$i_sub ( No.$newno )
日時：$date
なまえ：$i_nam2

$mcom

スレッドを見る
$fullscript?&no=$no
--------------------------------------------------------
EOM

# 使えそうな変数
# $sub
# $new
# $newno
# $fullscript 新設
#	本文はあえて掲載しないというテもアリ。
#	ホスト名：$host
#	ブラウザ：$ENV{'HTTP_USER_AGENT'}
#	Ｅメール：$in{'email'}
#	ＵＲＬ  ：$in{'url'}
#	$mcom

	# 題名をBASE64化
	$msub = &base64($msub);

#	$notifybcc = "@maillist2";

	# 1通ずつ送信する
#	while (@maillist) {

	# sendmail送信
	open(MAIL,"| $sendmail -t -i") || &error("送信失敗");
	print MAIL "To: $notifyaddr\n";
	print MAIL "Bcc: ";

	# メールアドレスを展開
	$" = ',';
	print MAIL "@maillist2";
	print MAIL "\n";
	print MAIL "From: $notifyaddr\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $ver\n\n";
	foreach ( split(/\n/, $mbody) ) {
		&jcode'convert(*_, 'jis', 'sjis');
		print MAIL $_, "\n";
	}
	close(MAIL);

#	}
}

#-------------------------------------------------
#  BASE64変換
#-------------------------------------------------
#	とほほのWWW入門で公開されているルーチンを
#	参考にしました。( http://tohoho.wakusei.ne.jp/ )
sub base64 {
	local($sub) = @_;
	&jcode'convert(*sub, 'jis', 'sjis');

	$sub =~ s/\x1b\x28\x42/\x1b\x28\x4a/g;
	$sub = "=?iso-2022-jp?B?" . &b64enc($sub) . "?=";
	$sub;
}
sub b64enc {
	local($ch)="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	local($x, $y, $z, $i);
	$x = unpack("B*", $_[0]);
	for ($i=0; $y=substr($x,$i,6); $i+=6) {
		$z .= substr($ch, ord(pack("B*", "00" . $y)), 1);
		if (length($y) == 2) {
			$z .= "==";
		} elsif (length($y) == 4) {
			$z .= "=";
		}
	}
	$z;
}

#-------------------------------------------------
#  禁止ワードチェック
#-------------------------------------------------
sub no_wd {
	my ($flg, $badword);

	# 検索文字列を検索専用の変数に入れ、全て小文字に変換
	my $lc_searchwords = lc("$i_nam $i_sub $i_com $in{'url'}");

	foreach ( split(/,/, $no_wd) ) {
		chomp($_);

		# 検索実行
		if (index($lc_searchwords, lc($_)) >= 0) {
			# 検索された文字列を記録
			if ($badwordlog) {
				open(my $out_fh, '>>', $badwordlog) || &error("Write Error: $badwordlog");
				flock($out_fh, 2);
				print $out_fh "$_\t$i_nam\t$i_sub\t$i_com\t$in{'url'}\t$date\t$time\t$host\n";
				close($out_fh);
			}
			$badword = $_;
			$flg = 1;
			last;
		}
	}

	if ($flg) { &error("禁止ワード $badword が含まれています"); }
}

#-------------------------------------------------
#  名前欄のNGワード処理(禁止文字列・入力許可文字チェック)
#-------------------------------------------------
sub ng_nm {
	if($ng_nm || @permit_name_regex) {
		my $ng_flg = 0;

		# NGワード処理からトリップキーを除外し、内部文字列に変換
		my $utf8flagged_name = $enc_cp932->decode((split(/#/, $i_nam, 2))[0]);

		# $ng_nmで設定された禁止文字列が含まれていないかどうかチェック
		if($ng_nm) {
			foreach my $check_target (split(/,/, $ng_nm)) {
				# 設定された禁止文字列をそれぞれ内部文字列に変換してからチェック
				if(index($utf8flagged_name, $enc_cp932->decode($check_target)) != -1) {
					$ng_flg = 1;
					last;
				}
			}
		}

		# 入力された文字が全て許可されているかどうかチェック
		if(!$ng_flg && @permit_name_regex) {
			# 許可文字の正規表現文字クラスを作成
			my $permit_name_regex_charclass = '^[' . join('', @permit_name_regex) . ']*$';

			# 名前欄で入力された文字が全て許可されているかどうかチェック
			$ng_flg ||= $utf8flagged_name !~ /(?:^$|${permit_name_regex_charclass})/;
		}

		# 禁止文字列あるいは、入力が許可されていない文字が見つかった時のエラー表示
		if($ng_flg) {
			&error("名前欄「 $i_nam 」は書き込みできません。");
		}
	}
}

#-------------------------------------------------
#  日本語チェック
#-------------------------------------------------
sub jp_wd {
	local($sub, $com, $mat1, $mat2, $code1, $code2);
	$sub = $i_sub;
	$com = $i_com;

	if ($sub) {
		($mat1, $code1) = &jcode'getcode(*sub);
	}
	($mat2, $code2) = &jcode'getcode(*com);
	if ($code1 ne 'sjis' && $code2 ne 'sjis') {
		&error("題名又はコメントに日本語が含まれていません");
	}
}

#-------------------------------------------------
#  URL個数チェック
#-------------------------------------------------
sub urlnum {
	local($com) = $i_com;
	local($num) = ($com =~ s|(https?://)|$1|ig);
	if ($num > $urlnum) {
		&error("コメント中のURLアドレスは最大$urlnum個までです");
	}
}


#-------------------------------------------------
#  メール送信（ユーザー間）
#-------------------------------------------------
sub mailsend {
	# チェック
	if (!$usermail) {
		&error("ユーザー間のメール送信機能\は無効になっています。");
	}

	# 汚染チェック
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# 報告種別判定
	# 1: コメント報告  2: 違反スレッド報告  3: 警告スレッド報告
	my $type = exists($in{'type'}) ? int($in{'type'}) : 0;
	if ($type < 1 || $type > 3 || ($type == 1 && !exists($in{'no'}))) {
		error("不正なアクセスです");
	}

	# 対象レスNo決定
	my $target_res_no = $in{'type'} == 1 ? int($in{'no'}) : 1;

	# 投稿内容チェック
	if ($no_wd) { &no_wd; }
	if ($i_com ne '' && $jp_wd) {
		# jp_wdサブルーチンを転用
		my ($mat, $code) = &jcode'getcode(*i_com);
		if ($code ne 'sjis') {
			error('コメントに日本語が含まれていません');
		}
	}
	if ($urlnum > 0) { &urlnum; }
	if ($i_nam eq "") {
		if ($in_name) { &error("名前は記入必須です"); }
		else { $i_nam = '名無し'; }
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/)
	{ &error("名前は正しく記入してください"); }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/)
	{ &error("コメントは正しく記入してください"); }

	# 投稿キーチェック
	if ($regist_key_res) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			&error("投稿キーが入力不備です。<p>投稿フォームに戻って再読込み後、指定の数字を入力してください");
		}

		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
		my ($chk) = &registkey_chk($in{'regikey'}, $in{'str_crypt'});
		if ($chk == 0) {
			&error("投稿キーが制限時間を超過しました。<p>投稿フォームに戻って再読込み後、指定の数字を再入力してください");
		} elsif ($chk == -1) {
			&error("投稿キーが不正です。<p>投稿フォームに戻って再読込み後、指定の数字を入力してください");
		}
	}

	# プライベートブラウジングモードであるかどうか
	my $is_private_browsing_mode = (exists($in{'pm'}) && $in{'pm'} eq '1') ? 1 : 0;

	# CookieAインスタンス初期化
	my $cookie_a = UniqueCookie->new($cookie_current_dirpath);

	# CookieA保持チェック
	if (!$cookie_a->is_issued()) {
		error("送信できません");
	}

	# CookieA 値取得
	my $cookiea_value = $cookie_a->value();

	# Cookieに保存されている登録IDを取得
	my $cuser_id = (get_cookie())[5];

	# 書込IDを取得
	my $chistory_id = HistoryCookie->new()->get_history_id();

	# ホストとUserAgentを判定するユーザーであるかどうかを判定
	my $judge_host_ua_flg = 1;
	foreach my $exclude_host (@ngthread_thread_list_creator_name_override_exclude_hosts) {
		if (index($host, $exclude_host) >= 0) {
			$judge_host_ua_flg = 0;
			last;
		}
	}

	# メール送信拒否ユーザー判定
	foreach my $setting_set_str (@usermail_prohibit) {
		# 設定文字列を分割
		my @setting_set_array = @{$mu->number_of_elements_fixed_split($setting_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@setting_set_array) != 4) {
			next;
		}

		# プライベートモード判定
		if ($setting_set_array[2] eq '1' && !$is_private_browsing_mode) {
			next;
		}

		# ホストとUserAgent・CookieA or 登録ID or 書込IDの設定文字列について、「-」を空に置き換え
		foreach my $i (0, 1) {
			$setting_set_array[$i] =~ s/^-$//;
		}

		# ホストとUserAgentか、CookieA or 登録ID or 書込IDのいずれかで一致したかどうかのフラグ
		my $host_useragent_or_cookiea_userid_historyid_matched_flg;

		# ホストとUserAgentの一致判定
        my ($host_useragent_match_array_ref) =
			@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
        $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);

		# CookieA or 登録ID or 書込IDの一致判定
		if (!$host_useragent_or_cookiea_userid_historyid_matched_flg && $setting_set_array[1] ne '') {
			my ($cookiea_userid_historyid_match_array_ref) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookiea_value, $cuser_id, $chistory_id, $setting_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
		}

		# 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
		# どちらかで一致したときは、エラー表示する
		if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
			error("送信できません");
		}
	}

	# mail.log 読み込み・連続送信制限・同一レス連続報告制限判定
	my @maillog;
	open(my $maillog_fh, '+<', $mailfile) || error("Open Error: $mailfile");
	flock($maillog_fh, 2) || error("Lock Error: $mailfile");
	seek($maillog_fh, 0, 0);
	while (<$maillog_fh>) {
		chomp($_);
		my ($maillog_thread_num, $maillog_res_num, $maillog_host, $maillog_useragent,
			$maillog_cookiea, $maillog_userid, $maillog_history_id, $maillog_time) = split(/<>/, $_);
		# $usermail_time_of_continuously_send_restrictingを経過したログ行は
		# ログに残さず、制限判定を行わない
		if ($maillog_time + $usermail_time_of_continuously_send_restricting <= $time) {
			next;
		}

		# 同一ユーザーの場合のみ、制限判定を行う
		if (($judge_host_ua_flg && $maillog_host eq $host && $maillog_useragent eq $useragent)
			|| $maillog_cookiea eq $cookiea_value
			|| ($maillog_userid ne '-' && $maillog_userid eq $cuser_id)
			|| ($maillog_history_id ne '-' && $maillog_history_id eq $chistory_id)
		) {
			# 制限判定
			# 連続送信制限判定 ($mailwait)
			# 同一レス連続報告制限判定 ($usermail_time_of_continuously_send_restricting)
			if ($maillog_time + $mailwait > $time
				|| ($maillog_thread_num == $in{'f'} && $maillog_res_num == $target_res_no)
			) {
				error("連続送信はもうしばらく時間をおいて下さい");
			}
		}

		# 制限に該当しない場合は、残すログ行として配列に追加
		push(@maillog, $_);
	}
	seek($maillog_fh, 0, 0);

	# スレッドログファイルオープン
	my $thread_logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(my $threadlog_fh, '<', $thread_logfile_path) || error("Open Error: $in{'f'}.cgi");
	flock($threadlog_fh, 1) || error("Lock Error: $in{'f'}.cgi");

	# スレッドログファイル先頭行を取得し、スレッド名・レス数を取得
	my $top = <$threadlog_fh>;
	chomp($top);
	my ($thread_sub, $num_of_res) = (split(/<>/, $top))[1, 2];
	$thread_sub =~ s/\0*//g;  # スレッド名に含まれているnull文字(\0)を削除
	if ($num_of_res == 0) {
		$num_of_res = 1;
	}

	# コメント報告の場合は指定レス、それ以外の場合は、スレッド先頭レスの
	# 名前・ホスト名・コメント・CookieA・登録ID・書込ID・画像アップ枚数を取得する
	my ($res_name, $res_comment, $res_host, $res_cookiea, $res_userid, $res_historyid, $res_num_of_img);
	my $res_found_flg;
	if ($type != 1 || $target_res_no <= $num_of_res) {
		while (<$threadlog_fh>) {
			chomp($_);
			my @res = split(/<>/, $_);
			if ($type != 1 || $res[0] == $target_res_no) {
				($res_name, $res_comment, $res_host, $res_userid, $res_cookiea, $res_historyid) = @res[2, 4, 6, 16, 18, 19];
				$res_num_of_img = scalar(grep { $_ !~ qr/^,/ } @res[12..14]);
				$res_found_flg = 1;
				last;
			} elsif ($res[0] > $target_res_no) {
				last;
			}
		}
	}
	if (!$res_found_flg) {
		error("該当するレスが見つかりません");
	}

	# スレッドログファイルクローズ
	close($threadlog_fh);

	# mail.logに記録しないユーザーの判定
	my $maillog_record_flg = 1;
	foreach my $setting_set_str (@usermail_not_record) {
		# 設定文字列を分割
		my @setting_set_array = @{$mu->number_of_elements_fixed_split($setting_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@setting_set_array) != 4) {
			next;
		}

		# プライベートモード判定
		if ($setting_set_array[2] eq '1' && !$is_private_browsing_mode) {
			next;
		}

		# ホストとUserAgent・CookieA or 登録ID or 書込IDの設定文字列について、「-」を空に置き換え
		foreach my $i (0, 1) {
			$setting_set_array[$i] =~ s/^-$//;
		}

		# ホストとUserAgentか、CookieA or 登録ID or 書込IDのいずれかで一致したかどうかのフラグ
		my $host_useragent_or_cookiea_userid_historyid_matched_flg;

		# ホストとUserAgentの一致判定
		if ($setting_set_array[0] ne '') {
			my ($host_useragent_match_array_ref) =
				@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);
		}

		# CookieA or 登録ID or 書込IDの一致判定
		if (!$host_useragent_or_cookiea_userid_historyid_matched_flg && $setting_set_array[1] ne '') {
			my ($cookiea_userid_historyid_match_array_ref) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookiea_value, $cuser_id, $chistory_id, $setting_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
		}

		# 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
		# どちらかで一致したときは、mail.logに記録しないユーザーとしてフラグを立てる
		if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
			$maillog_record_flg = 0;
			last;
		}
	}

	# mail.logに記録するユーザの場合は、@maillogにメールログを追加する
	if ($maillog_record_flg) {
		# mail.log記録の登録ID・書込IDを定義
		my $ml_user_id = (defined($cuser_id) && $cuser_id ne '') ? $cuser_id : '-';
		my $ml_history_id = defined($chistory_id) ? $chistory_id : '-';
		# 配列に追加
		unshift(@maillog, "$in{'f'}<>$target_res_no<>$host<>$useragent<>$cookiea_value<>$ml_user_id<>$ml_history_id<>$time<>");
	}

	# トリップ処理
	my $i_nam2 = &trip($i_nam);

	# メールタイトルを定義
	my $msub;
	if ($type == 1) {
		$msub = "違反コメント：$thread_sub";
	} elsif ($type == 2) {
		$msub .= "違反スレッド：$thread_sub";
	} else { # elsif ($type == 3)
		$msub .= "警告スレッド：$thread_sub";
	}
	if (!$maillog_record_flg) {
		# mail.logに記録しないユーザーの場合は、メールタイトル末尾に●を追加
		$msub .= "●";
	}

	# 本文の改行・タグを復元
	$res_comment =~ s/<br>/\n/g;
	$res_comment =~ s/&lt;/</g;
	$res_comment =~ s/&gt;/>/g;
	$res_comment =~ s/&quot;/"/g;
	$res_comment =~ s/&amp;/&/g;

	# ユーザーコメントの改行・タグを復元
	my $user_comment = $i_com;
	$user_comment =~ s/<br>/\n/g;
	$user_comment =~ s/&lt;/</g;
	$user_comment =~ s/&gt;/>/g;
	$user_comment =~ s/&quot;/"/g;
	$user_comment =~ s/&amp;/&/g;

	# メール本文を定義
	my $mbody = "スレッド名：$thread_sub\n";
	if ($type == 1) {
		$mbody .= "違反コメントURL：$fullscript?mode=view&no=$in{'f'}&l=$in{'no'}\n";
		$mbody .= "URL：$fullscript?mode=view&no=$in{'f'}\n";
	} elsif ($type == 2) {
		$mbody .= "違反スレッドURL：$fullscript?mode=view&no=$in{'f'}\n";
	} else { # elsif ($type == 3)
		$mbody .= "警告スレッドURL：$fullscript?mode=view&no=$in{'f'}\n";
	}
	if ($type != 3 && $in{'category'} ne '-') {
		$mbody .= "種類：$in{'category'}\n";
	}
	$mbody .= <<"EOM";

【報告】
名前：$res_name
ホスト：$res_host
CookieA：$res_cookiea
EOM
	## 対象レスのログに記録がある登録ID・書込IDと、画像アップ枚数(1枚以上の場合のみ)を本文に追加
	if ($res_userid ne '') {
		$mbody .= "登録ID：$res_userid\n";
	}
	if ($res_historyid ne '') {
		$mbody .= "書込ID：$res_historyid\n";
	}
	if ($res_num_of_img > 0) {
		$mbody .= "画像アップ：${res_num_of_img}枚\n";
	}
	$mbody .= <<"EOM";
本文：
$res_comment

【送信者】
CookieA：$cookiea_value
EOM
	## 送信者が登録ID・書込IDを保持している場合は、その項目を本文に追加
	if (defined($cuser_id) && $cuser_id ne '') {
		$mbody .= "登録ID：$cuser_id\n";
	}
	if (defined($chistory_id)) {
		$mbody .= "書込ID：$chistory_id\n";
	}
	$mbody .= <<"EOM";
ホスト名：$host
UserAgent：$useragent
EOM
	## 送信者がプライベートモードで送信した場合は、その項目を本文に追加
	if ($is_private_browsing_mode) {
		$mbody .= "プライベートモード：有効\n";
	}
	$mbody .= <<"EOM";
ユーザーコメント：
$user_comment
EOM

	# 宛名・差出人・件名・X-Mailerを内部エンコードに変換後、Base64エンコードされたUTF-8のMIMEヘッダー表記にする
	my $enc_mimeheader = Encode::find_encoding('MIME-Header'); # MIMEヘッダー用 Encodeインスタンス作成
	my $mail_header_to = $enc_mimeheader->encode($enc_cp932->decode($usermail_to_address));
	my $mail_header_from = $enc_mimeheader->encode($enc_cp932->decode("\"$i_nam2\" <$usermail_to_address>"));
	my $mail_header_subject = $enc_mimeheader->encode($enc_cp932->decode($msub));
	my $mail_header_mailer = $enc_mimeheader->encode($enc_cp932->decode($ver));

	# 日付ヘッダーを作成
	my $mail_header_date = strftime("%a, %d %b %Y %H:%M:%S %z", @localtime);

	# 本文をBase64エンコードされたUTF-8に変換
	my $base64_body = encode_base64(Encode::encode_utf8($enc_cp932->decode($mbody)));

	# sendmail送信
	open(my $sendmail_ph, '|-', "$sendmail -t") || &error("送信失敗");
	print $sendmail_ph <<"EOM";
To: $mail_header_to
From: $mail_header_from
Subject: $mail_header_subject
Date: $mail_header_date
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: base64
X-Mailer: $mail_header_mailer

$base64_body
EOM
	close($sendmail_ph);

	# 完了メッセージ
	&header;
	print <<EOM;
<br><br><div align="center">
<Table border=0 cellspacing=0 cellpadding=0 width="400">
<Tr><Td bgcolor="$col1">
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center" height=60>
	<h3 style="font-size:15px">メールを送信しました</h3>
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
EOM

	# 戻りフォーム
	print <<"EOM";
<table>
<tr>
  <td valign=top>
    <a href="$bbscgi"><button type="button">掲示板へ戻る</button></a>
  </td>
  <td width=15></td>
  <td valign=top>
    <a href="$readcgi?mode=view&no=$in{'f'}"><button type="button">スレッドへ戻る</button></a>
  </td>
</tr>
</table>
</div>
</body>
</html>
EOM

	# メールログ更新
	seek($maillog_fh, 0, 0);
	print $maillog_fh join("\n", @maillog) . "\n";
	truncate($maillog_fh, tell($maillog_fh));
	close($maillog_fh);

	exit;
}

#-------------------------------------------------
#  FAQ実現のために参照されているスレッド番号を記録
#-------------------------------------------------

sub faqcount {
# 引数受け取り コメント文、スレッド番号
#	local($msg, $faqf) = @_;
#		&faqcount ($i_com,$in{'res'});
	local($flag,@faqs);
	local ($msg, $faqf);
	$msg = $i_com;
	$faqf= $in{'res'};
# コメント文から、参照先スレッド番号を抽出して配列へ
#	@faqs =~ /(?:$fullscript)(?:[^n\"]*)no=(\d+)/;
#	@faqs = /no=(\d+)/;
#	while ($word =~ /(.)/g){ push(@word, $1); }
	while ($msg =~ /no=(\d+)/g){ push(@faqs, $1); }

# テストなんでとりあえず１個
#	$faq = $1;
#	$faq = 2;

	foreach $faq (@faqs) {
		chomp($faq);
#	if ($faq) {
# FAQのカウントをするファイル
$faqfile = "./faq.log";
# スレッドNo<>参照しているスレッドNo1,No2,No3,,,<>

			# FAQ管理ファイルから該当スレッド抜き出し
			my $new_log;
			open(DAT,"+< $faqfile") || &error("Open Error: $faqfile");
			eval "flock(DAT, 2);";

			$flag=0;
			while(<FAQ>) {
				chomp($_);
				local($no,$refs) = split(/<>/);
				if ($faq == $no) {
					local(@array) = split(/\,/, $refs);
					local(@tmp);
					for (@array){$tmp[$_]=1;}
					if ($tmp[$faqf]) {
						$new_log = "$_\n" . $new_log;
					} else {
						$new_log = "$faq<>$refs,$faqf<>\n" . $new_log;
					}
				$flag++;
				} else {
					$new_log = "$_\n" . $new_log;
				}
			}

			if (!$flag) {
				$new_log = "$faq<>$faqf<>\n" . $new_log;
			}

			# 現行ログindex更新
			seek(FAQ, 0, 0);
			print FAQ $new_log;
			truncate(FAQ, tell(FAQ));
			close(FAQ);
	}
}

#-------------------------------------------------
#  スレッド作成数/レス投稿数ログファイル カウントアップ
#-------------------------------------------------
sub regist_log_countup {
	my ($logfile) = @_;

	# ログファイルが存在し、読み書きを行える時のみカウントアップする
	if(-f $logfile && -r $logfile && -w $logfile) {
		open(my $fh, '+<', $logfile) || return;
		if(flock($fh, 2)) { # ロック失敗時は書き込まない
			my $log;
			my $date = strftime('%Y/%m/%d', @localtime); # 今日の日付をフォーマット

			# カウントを作成
			my $count = 0;
			my $top = <$fh>;
			my @tops = split(/[ 件\n]/, $top);
			if(scalar(@tops) == 2 && $tops[0] eq $date && $tops[1] =~ /^\d*$/) {
				# ログファイルの先頭行が同日で正しいフォーマットだった場合に、
				# 記録されているカウントを取得
				$count = $tops[1];
			} else {
				$log .= $top;
			}
			$count++; # カウントアップ
			$log = "$date $count件\n" . $log;

			# ログファイルの残りの行を読み込む
			{
				local $/ = undef;
				$log .= <$fh>;
			}

			# ログファイルに書き込み
			seek($fh, 0, 0);
			print $fh $log;
			truncate($fh, tell($fh));
		}
		close($fh);
	}
}

# NGスレッド機能 スレッド作成者の名前上書き 対象判定サブルーチン
sub ngthread_name_override_judge {
	my ($name, $user_id, $cookie_a, $history_id, $parent_res_log_array_ref) = @_;

	# レスログ行パース
	# >>1のホスト・登録ID・CookieA・書込IDをログ行から読み取り
	my ($parent_res_host, $parent_res_user_id, $parent_res_cookie_a_value, $parent_res_history_id) = @{$parent_res_log_array_ref}[6,16,18,19];

	# 名前除外判定
	if (grep { $_ ne '' && index($name, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_names) {
		return 0;
	}

	# ホスト同一判定
	if (scalar(grep { $_ ne '' && index($host, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0
		&& $parent_res_host ne '' && $host eq $parent_res_host) {
		return 1;
	}

	# 登録ID同一判定
	if ($parent_res_user_id ne '' && $user_id eq $parent_res_user_id) {
		return 1;
	}

	# CookieA同一判定
	if ($parent_res_cookie_a_value ne '' && $cookie_a->value() eq $parent_res_cookie_a_value) {
		return 1;
	}

	# 書込ID同一判定
	if ($parent_res_history_id ne '' && $history_id eq $parent_res_history_id) {
		return 1;
	}

	# いずれの項目にも一致しなかった
	return 0;
}

# 投稿時の名前の消去機能 対象判定サブルーチン
sub is_remove_name_target_post {
	my ($thread_title, $raw_name, $host, $useragent, $cookie_a, $user_id, $history_id, $target_settings_array_ref) = @_;
	if (ref($target_settings_array_ref) ne 'ARRAY') {
		return;
	}

	SET_LOOP: foreach my $raw_target_set_str (@{$target_settings_array_ref}) {
		# 「:」で区切って配列とする
		my @target_set_array = @{$mu->number_of_elements_fixed_split($raw_target_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@target_set_array) != 4) {
			next SET_LOOP;
		}

		# 「-」のみの場合に「」(空)に置き換える
		for (my $i=0; $i<4; $i++) {
			$target_set_array[$i] =~ s/^-$//;
		}

		# スレッド名判定
		my ($title_match_array_ref) =
			@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $target_set_array[0], undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (!defined($title_match_array_ref)) {
			# 対象スレッド名設定がない場合や、設定に合致しなかった場合はセットをスキップ
			next SET_LOOP;
		}

		# 名前判定
		if (!defined($mu->get_matched_name_to_setting($raw_name, $target_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			# 対象の名前の設定がない場合や、名前が一致しなかった場合はセットをスキップ
			next SET_LOOP;
		}

		# ホストとUserAgentの組み合わせ判定・CookieA or 登録ID or 書込ID判定で
		# 否定指定による一致判定を行ったかどうか
		my $is_not_match = 0;

		# ホストとUserAgentの組み合わせ判定
		my @host_useragent_match = (0, -1);
		if ($target_set_array[2] ne '') {
			my ($host_useragent_match_array, undef, $not_match_flg) =
				@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $target_set_array[2], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			@host_useragent_match = (defined($host_useragent_match_array), $not_match_flg);
			$is_not_match ||= $not_match_flg;
		}

		# CookieA or 登録ID or 書込ID判定
		my @cookiea_userid_historyid_match = (0, -1);
		if ($target_set_array[3] ne '') {
			my ($cookiea_userid_historyid_match_array, $not_match_flg) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $target_set_array[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			@cookiea_userid_historyid_match = (defined($cookiea_userid_historyid_match_array), $not_match_flg);
			$is_not_match ||= $not_match_flg;
		}

		# 一致判定 or 否定指定による不一致判定で判定結果を絞り、制限対象かどうか判定
		if ($is_not_match == 0) {
			# 通常の一致判定の場合
			# (いずれかに一致の場合)
			if (scalar(grep { ${$_}[1] == $is_not_match && ${$_}[0] } (\@host_useragent_match, \@cookiea_userid_historyid_match)) > 0) {
				return 1;
			}
		} else { # $is_not_match == 1
			# 否定指定による不一致判定の場合
			# (全て不一致の場合)
			my @not_match_items = grep { ${$_}[1] == $is_not_match } (\@host_useragent_match, \@cookiea_userid_historyid_match);
			if (scalar(@not_match_items) > 0 && scalar(grep { ${$_}[0] } @not_match_items) == scalar(@not_match_items)) {
				return 1;
			}
		}
	}

	# いずれの設定にも一致しなかった
	return;
}

# 書き込みログの置換記録機能 置換判定・置換後文字列作成サブルーチン
sub replace_contents_for_post_log {
	my ($original_contents) = @_;

	# 空の場合は一致判定を行わない
	if ($original_contents eq '') {
		return $original_contents;
	}

	# 一致判定
	my @matched_str_array; # 一致した変換後文字列の配列
	my $original_contents_array_ref_for_matching = [$original_contents]; # 一致判定で使用するためのオリジナル文字列の配列リファレンス
	foreach my $raw_replace_set_str (@post_log_contents_replace) {
		# 内部エンコードに変換し、「:」で区切る
		my $utf8flagged_replace_set_str = $enc_cp932->decode($raw_replace_set_str);
		my ($find_str, $replace_str) = split(/:/, $utf8flagged_replace_set_str, 2);
		if ($find_str eq '' || !defined($replace_str)) {
			# 検索文字列が空か、置換文字列が定義されていないときはスキップ
			next;
		}

		# 一致判定
		if (defined($mu->universal_match($original_contents_array_ref_for_matching, [$find_str], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			# 一致したら、変換後文字列をCP932に戻して配列に追加
			push(@matched_str_array, $enc_cp932->encode($replace_str));
		}
	}

	# 置換後文字列を返す
	if (scalar(@matched_str_array) > 0) {
		# 1つ以上の設定値と一致していたら、配列を「;」で結合した文字列を返す
		return join(';', @matched_str_array);
	} else {
		# 1つも一致していなかったら、オリジナル文字列を返す
		return $original_contents;
	}
}

# 重複投稿処理判定サブルーチン
sub is_duplicate_post {
	my ($thread_title,
		$img_upload_flg, $com, $cookie_a, $user_id, $history_id, $host,
		$lastres_com, $lastres_cookie_a, $lastres_user_id, $lastres_history_id, $lastres_host,
		$settings_array_ref) = @_;

	# 投稿本文・最終レス本文一致判定
	if ($com ne $lastres_com || ($img_upload_flg && $com eq '')) {
		# 一致しなかったか、画像投稿があり本文がない場合は、重複投稿ではない
		return;
	}

	# CookieA or 登録ID or 書込ID or ホスト一致フラグ
	my $cookiea_userid_historyid_host_matched_flg;

	# 投稿CookieA・最終レスCookieA一致判定
	if (defined($cookie_a) && $cookie_a ne '' && $cookie_a eq $lastres_cookie_a) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# 投稿登録ID・最終レス登録ID一致判定
	if (!$cookiea_userid_historyid_host_matched_flg && defined($user_id) && $user_id ne '' && $user_id eq $lastres_user_id) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# 投稿書込ID・最終レス書込ID一致判定
	if (!$cookiea_userid_historyid_host_matched_flg && defined($history_id) && $history_id ne '' && $history_id eq $lastres_history_id) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# 投稿ホスト・最終レスホスト一致判定
	# (@ngthread_thread_list_creator_name_override_exclude_hostsと最終レスホストが中間一致する場合は判定を行わない)
	if (!$cookiea_userid_historyid_host_matched_flg
		&& scalar(grep { $_ ne '' && index($lastres_host, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0
		&& $host eq $lastres_host
	) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# CookieA or 登録ID or 書込ID or ホストのいずれにも一致しない場合は、重複投稿ではない
	if (!$cookiea_userid_historyid_host_matched_flg) {
		return;
	}

	# スレッド名一致判定
	my $normal_matched_flg;
	foreach my $settings_str (@{$settings_array_ref}) {
		my @thread_match_result =
			@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $settings_str, undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if ($thread_match_result[1] == 1) {
			# 否定一致
			if (!defined($thread_match_result[0])) {
				# 否定条件のいずれかに一致したため、重複投稿処理を行わない
				return;
			}
			# 通常条件のみで再度検索
			@thread_match_result =
				@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $settings_str, 1, undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		}
		# 通常一致判定
		$normal_matched_flg ||= defined($thread_match_result[0]);
	}

	return $normal_matched_flg;
}
