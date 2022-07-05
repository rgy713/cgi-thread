#!/usr/bin/perl

# きりしま式 Web Patio v3.4 k1.00

#┌─────────────────────────────────
#│ [ WebPatio 書き込み履歴表示CGI ]
#│ history.cgi - based on patio.cgi 2011/04/08
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

BEGIN {
	# 外部ファイル取り込み
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use NGThread;
use HistoryCookie;
use HistoryLog;

&parse_form;
if ($mode eq "check") {
	require $checkpl;
	&check;
}

&axscheck;
if ($mode eq "find") {
	require $findpl;
	&find;
}
elsif ($mode eq "enter_disp") { &enter_disp; }
elsif ($mode eq "logoff") { &logoff; }
elsif ($mode eq "ngthread_display_mode") { set_ngthread_display_mode(); }
elsif ($mode eq "ngthread_words") { set_ngthread_words(); }
elsif ($mode eq "delete_post_history" && $postflag) { delete_post_history(); }
&history_list_view;

#-------------------------------------------------
#  メニュー部表示
#-------------------------------------------------
sub history_list_view {
	local($alarm,$i,$top);

	# アラーム数定義
	$alarm = int ( $m_max * 0.9 );

	# 書込IDを取得
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};

	# 書込IDログイン済みの場合、HistoryLogインスタンスを初期化
	my $history_log = defined($chistory_id) ? HistoryLog->new($chistory_id) : undef;

	# NGスレッド設定読み込み
	my $ngthread = do {
		if (defined($history_log)) {
			# HistoryLogインスタンスが初期化済みの場合、書込IDログを使用するよう初期化
			NGThread->new($history_log);
		} else {
			# それ以外の場合は、Cookieを使用するよう初期化
			NGThread->new();
		}
	};
	my $ngthread_display_mode = $ngthread->get_display_mode();

	&header();
	print <<"EOM";


<STYLE type="text/css">
<!--

*{
	margin:0px;
	padding:0px;
}





table#teeest{
  background-color:#ffffff;
/*  border: 1px solid #64bf64;	*/
  border-collapse: collapse;
  max-width:100%;
}

table#teeest tr{
/*  border: 1px solid #64bf64;	*/
}
table#teeest td {
  border-bottom: 1px solid #64bf64;
}

#wrapper-main-in-table{
	margin:20px;
}

blockquote{
	margin:10px 0px;
}


tr.test6 a,
tr.test2 a,
tr.test7 a,
tr.test1 a,	/* 管理者ロック */
tr.test3 a,	/* 	スレッド落ち寸前マーク */
tr.test5 a,
td.test5 a {
	display:block;
	width:100%;
	color:#000000 !important;
	padding:10px;
}

p.thread{
}
p.thread a:link,
p.thread a:visited{
	color:#888888;
	padding:8px 0px 8px 6px;
	display:block;
	text-decoration:none;
}
/*
p.thread a:visited{
	color:#ff8c00;
}
*/


.td1{
	border-bottom:1px solid #cbcbcb;
	width:100%;
}
.td2{
	border-bottom:1px solid #cbcbcb;
	background-color:#fafafa;
}

tr.ngthread { color: #e6e6e6; }
tr.ngthread a { color: #e6e6e6 !important; }

td.new_res_exists { color: #ff0000; }
tr.ngthread td.new_res_exists { color: #ffe5e5; }

#edit_toggle         { display: none; }
#edit_toggle:link    { color: #0000ff; }
#edit_toggle:visited { color: #0000ff; }
#edit_toggle:hover   { color: #0000ff; }
#edit_toggle::active { color: #0000ff; }
#edit_toggle.enabled { color: #ff0002; }
.edit_elements       { display: none; }

-->
</STYLE>


<div align="center">
<table width="95%" border="0">
<tr>
  <td>
	<table width="100%">
	<tr>
	<td><b style="font-size:$t_size; color:$t_color">$title</b><br>
<small>$desc</small></td><td align="right">
EOM

# Google AdSense
	&googleadsense;

	print <<"EOM";
</td>
EOM

	if ($authkey) {
		print "<td align=\"right\">ようこそ、<b>$my_nameさん</b></td>\n";
	}

	print <<EOM;
	</tr>
	</table>
  </td>
</tr>
<tr bgcolor="$col1">
  <td align="right" nowrap>
EOM

	if (!$createonlyadmin) {
	print <<EOM;
	<font color="$col2">|</font>
	<a href="$readcgi?mode=form"><font color="$col2">新規スレッド</font></a>
EOM
} else {
	print <<EOM;
	<font color="$col2">|</font>
	<font color="$col2">スレッド作成制限中</font>
EOM
}

	print <<EOM;
	<font color="$col2">|</font>
	<a href="$history_webprotect_issue_url" target="_top"><font color="$col2">書込書込ID発行・認証</font></a>
	<font color="$col2">|</font>
	<a href="$historycgi" target="_top"><font color="$col2">書込履歴</font></a>
	<font color="$col2">|</font>
	<a href="$home" target="_top"><font color="$col2">ホームに戻る</font></a>
	<font color="$col2">|</font>
	<a href="$notepage"><font color="$col2">留意事項</font></a>
	<font color="$col2">|</font>
	<a href="$bbscgi?mode=find"><font color="$col2">ワード検索</font></a>
	<font color="$col2">|</font>
	<a href="$readcgi?mode=past"><font color="$col2">過去ログ</font></a>
	<font color="$col2">|</font>
EOM

	# 認証モードのとき
	if ($authkey) {
		print "<a href=\"$bbscgi?mode=logoff\"><font color=\"$col2\">ログオフ</font></a>\n";
		print "<font color=\"$col2\">|</font>\n";
	}

	print <<EOM;
	<a href="$admincgi"><font color="$col2">管理用</font></a>
	<font color="$col2">|</font>&nbsp;&nbsp;&nbsp;
  </td>
</tr>
</table>
EOM

# 閲覧専用モード

if ( $ReadOnly ) {
	print <<EOM;
<p>
<Table border=0 cellspacing=0 cellpadding=0 width="95%">
<Tr><Td>
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr><td>
	<p align="left">$Oshirase</p>
</td>
</tr></table>
</Td></Tr></Table>
EOM

}

	my $edit_toggle_add_class_str = $in{'edit'} ? ' class="enabled"' : '';
	print <<EOM;
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="delete_post_history">
<br>
<h1>書き込み履歴</h1>
<br>
<a href="#" id="edit_toggle"$edit_toggle_add_class_str>編集する</a><br><br>
<span class="edit_elements">
    <button type="button" id="edit_all_select">すべて選択</button>&nbsp;&nbsp;&nbsp;&nbsp;
    <input type="submit" value="選択したスレッドを削除"><br><br>
</span>

<Table border="0" cellspacing="0" cellpadding="0" id="index_table">
<Tr><Td>
<table id="teeest" border="0" cellspacing="0" cellpadding="5" width="100%">
<tr bgcolor="#bfecbf" class="thth">
  <td bgcolor="#bfecbf" class="center">ジャンプ</td>
  <td bgcolor="#bfecbf" class="">スレッド名</td>
  <td bgcolor="#bfecbf" class="center">新着数</td>
  <td bgcolor="#bfecbf" class="center">レス数</td>
EOM

	if ($p eq "") { $p = 0; }
	$i = 0;

	# 書き込み履歴ログ表示 (書込IDログイン済状態の場合のみ)
	if (defined($history_log)) {
		# 存在するスレッド情報を取得
		my @post_history = @{$history_log->get_post_histories()};

		# 存在するスレッドで、表示対象であればスレッド情報を出力
		foreach my $thread_info_array_ref (@post_history) {
			# 履歴記録時点スレッド情報取得
			my ($thread_no, $res_no, $res_time) = @{$thread_info_array_ref};

			# スレッドログファイルパス決定
			my $logfile_path = get_logfolder_path($thread_no) . "/$thread_no.cgi";

			# スレッドログファイルを開けるかどうか
			if (-r $logfile_path) {
				# カテゴリ表示機能 無効時
				# 表示範囲外の場合はスキップ
				if ($in{'k'} eq '' && ($i < $p || $i > $p + $history_display_menu - 1)) {
					$i++; # 存在スレッド数インクリメント
					next;
				}

				# スレッド情報取得
				open(my $log_fh, '<', $logfile_path) || error("Open Error: $thread_no.cgi");
				flock($log_fh, 1) || error("Lock Error: $thread_no.cgi");
				my $log_top = <$log_fh>;
				close($log_fh);
				chomp($log_top);
				my ($thread_creator_name, $sub, $res_count) = (split(/<>/, $log_top))[0..2];
				if ($res_count == 0) { $res_count = 1; } # スレッド作成直後は0になっているため、1とする
				$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
				my $orig_sub = $sub; # スレッドタイトルを別途保管

				# カテゴリ表示機能 有効時
				# タイトル末尾にカテゴリ名を含まないか、表示範囲外の場合はスキップ
				if ($in{'k'} ne '' && ((my $no_cat_match = $sub !~ /$in{'k'}$/) || ($i < $p || $i > $p + $history_display_menu - 1))) {
					if (!$no_cat_match) {
						# カテゴリ名を含み、表示範囲外の場合のみ
						# 存在スレッド数インクリメント
						$i++;
					}
					next;
				}

				# NGスレッド一致判定
				my $is_ngthread = 0;
				if ($ngthread->is_ng_thread_creator($thread_creator_name) || $ngthread->is_ng_thread_title($orig_sub)) {
					# 一致する場合
					if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
						# スレッド非表示の場合はスキップ
						$i++; # 存在スレッド数インクリメント
						next;
					} else {
						# スレッド名置換の場合は置き換える
						$is_ngthread = 1;
					}
				}

				# 新着レス件数算出
				my $new_res_count = $res_count - $res_no;

				# スレッド レス表示範囲決定
				my $x = ($res_count - 20) >= 0 ? ($res_count - 20) : 0;
				my $y = $res_count + 20;

				if ($key eq '0' || $key == 4) { $icon = 'fold3.gif';$test = 'test1';$test_td = 'test1_td';$locked = '【ロック中】'; }
				elsif ($key == 2) { $icon = 'look.gif';$test = 'test7';$test_td = 'test7_td';$locked = ''; }
				elsif ($key == 3) { $icon = 'faq.gif';$test = 'test2';$test_td = 'test2_td';$locked = ''; }
				elsif ($res >= $alarm) { $icon = 'fold5.gif';$test = 'test3';$test_td = 'test1_td';$locked = ''; }
				elsif ($upl) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test4_td';$locked = ''; }
				elsif (time < $restime + $hot) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test5_td';$locked = ''; }
				else { $icon = 'fold1.gif';$test = 'test6';$test_td = 'test6_td';$locked = ''; }

				if ($is_ngthread) {
					# NGスレッドの場合
					print "<tr class=\"$test ngthread\">";
				} else {
					print "<tr class=\"$test\">";
				}
				print "<td width=\"30\">";
				print "<p class=\"thread\"><a href=\"$readcgi?no=$thread_no#re\">>></a></p>";
				print "</td>";
				if ($is_ngthread) {
					# NGスレッドの場合
					print "<td width=\"\"><a href=\"$readcgi?no=$thread_no\">---</a></td>";
				} else {
					print "<td width=\"\"><a href=\"$readcgi?no=$thread_no\">$sub</a></td>";
				}
				if ($new_res_count > 0) {
					# 新着レスが1件以上ある場合
					print "<td align=\"center\" width=\"70px\" class=\"new_res_exists\">\n";
				} else {
					print "<td align=\"center\" width=\"70px\">\n";
				}
					print <<"EOM";
<input type=\"checkbox\" name=\"thread_no\" value=\"$thread_no\" class=\"edit_elements edit_checkbox\">
$new_res_count
</td>
EOM
				print "<td align=\"center\" width=\"70px\"><a href=\"$readcgi?no=$thread_no&l=$x-$y#$res_count\">$res_count</a></td>";
				print "</tr>";

				$i++; # 存在スレッド数インクリメント
			}
		}
	}

	print "</table></Td></Tr></Table>\n";
	print "</form>\n";


	# ページ移動ボタン表示
	if ($p - $history_display_menu >= 0 || $p + $history_display_menu < $i) {
		print "<br><br><table>\n";

		# 現在表示ページ/全ページ数表示
		my $pages = int(($i - 1) / $history_display_menu) + 1; # 全ページ数取得
		if ($p < 0) {
			# マイナスが指定された時は、1ページ目とする
			$p = 0;
		} elsif ($p + 1 > $i) {
			# 全スレッド件数より大きい値が指定された時は、最終ページ指定とする
			$p = ($pages - 1) * $history_display_menu;
		}
		my $current_page = int($p / $history_display_menu) + 1; # 現在表示ページ取得
		print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

		# 1ページ目・前後ページ・最終ページへのリンク
		my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
		print "<tr><td class=\"num\">";
		if ($current_page <= 1) {
			print "&lt;&lt;　前へ　";
		} else {
			my $prev_page = ($current_page - 2) * $history_display_menu;
			print "<a href=\"$historycgi?${k_html}p=0\">&lt;&lt;</a>　<a href=\"$historycgi?${k_html}p=$prev_page\">前へ</a>　";
		}
		if ($current_page >= $pages) {
			print "次へ　&gt;&gt;";
		} else {
			my $next_page = $current_page * $history_display_menu;
			my $last_page = ($pages - 1) * $history_display_menu;
			print "<a href=\"$historycgi?${k_html}p=$next_page\">次へ</a>　<a href=\"$historycgi?${k_html}p=$last_page\">&gt;&gt;</a>";
		}
		print "</td></tr>\n";

		print "</table>\n";
	}

	# 著作権表示（削除不可）

	# NGスレッド表示モード取得
	my $ngthread_display_mode_text = do {
		if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
			'スレッドを非表示';
		} else {
			'スレッド名を置換';
		}
	};
	# スレッド作成者のNG設定を取得
	my $ngthread_ng_thread_creator = $ngthread->get_ng_thread_creator();
	# スレッド名のNG設定を取得
	my $ngthread_ng_thread_title = $ngthread->get_ng_thread_title();
	# スレッド名のNGの除外設定を取得
	my $ngthread_ng_thread_title_exclude = $ngthread->get_ng_thread_title_exclude();
	print <<"EOM";
<br><br>

<!-- NGスレッド設定 -->
<blockquote style="background-color:#e6e6e6">
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="ngthread_display_mode">
<br>
<b>・NGスレッド表\示設定</b><br>
現在のNGスレッド表\示設定は「$ngthread_display_mode_text」です。<br>

<input type="radio" name="display_mode" value="0" id="ngthread_display_hide" required> <label for="ngthread_display_hide">スレッドを非表\示にする</label>&nbsp;&nbsp;
<input type="radio" name="display_mode" value="1" id="ngthread_display_replace"> <label for="ngthread_display_replace">スレッド名を置換する</label>
<p><input type="submit" value="　設定する　"></p>
</form>
<br><br>
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="ngthread_words">
<b>スレッド作成者のNG設定</b><br>
<textarea name="ng_thread_creator" rows="10" cols="40">$ngthread_ng_thread_creator</textarea>
<br><br>
<b>スレッド名のNG設定</b><br>
<textarea name="ng_thread_title" rows="10" cols="40">$ngthread_ng_thread_title</textarea>
<br><br>
<b>スレッド名のNGの除外設定</b><br>
<textarea name="ng_thread_title_exclude" rows="10" cols="40">$ngthread_ng_thread_title_exclude</textarea>
<p><input type="submit" value="　設定する　"></p>
</form>
</blockquote><!-- end of blockquote -->


<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2"><td bgcolor="$col2" align="center">
<img src="$imgurl/foldnew.gif"> 新しい書き込みのあるスレッド &nbsp;&nbsp;
<img src="$imgurl/fold1.gif" alt="標準スレッド"> 標準スレッド &nbsp;&nbsp;
<img src="$imgurl/fold6.gif" alt="添付あり"> 添付あり &nbsp;&nbsp;
<img src="$imgurl/fold3.gif" alt="ロック中"> ロック中（書込不可）&nbsp;&nbsp;
<img src="$imgurl/fold5.gif" alt="アラーム"> アラーム（返信数$alarm件以上）&nbsp;&nbsp;
<img src="$imgurl/faq.gif"> ＦＡＱスレッド&nbsp;&nbsp;
<img src="$imgurl/look.gif" alt="管理者メッセージ"> 管理者メッセージ
</td></tr></table></Td></Tr></Table><br><br>
<!-- 著作権表\示部・削除禁止 ($ver) -->
<span class="s1">
- <a href="http://www.kent-web.com/" target="_top">Web Patio</a> -
 <a href="http://kirishima.it/patio/" target="_top">きりしま式</a> -
</span></div>
</body>
</html>
EOM

	# HistoryLogインスタンス解放
	if (defined($history_log)) {
		$history_log->DESTROY();
	}

	exit;
}

#-------------------------------------------------
#  URLエンコード
#-------------------------------------------------
sub url_enc {
	local($_) = @_;

	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-------------------------------------------------
#  ログオフ
#-------------------------------------------------
sub logoff {
	if ($my_ckid =~ /^\w+$/) {
		unlink("$sesdir/$my_ckid.cgi");
	}
	print "Set-Cookie: patio_member=;\n";

	&enter_disp;
}

#-------------------------------------------------
#  NGスレッド表示設定
#-------------------------------------------------
sub set_ngthread_display_mode {
	my $value = int($in{'display_mode'});

	# 入力値チェック
	if ($value != NGThread::DisplayMode_Hide && $value != NGThread::DisplayMode_Replace) {
		error("不正な値です");
	}

	# Cookie保存
	my $ngthread = NGThread->new();
	$ngthread->set_display_mode($value);
	$ngthread->save();

	# 完了画面表示
	if ($value == NGThread::DisplayMode_Hide) {
		success('「スレッドを非表示」に設定しました。', $historycgi);
	} else {
		success('「スレッド名を置換」に設定しました。', $historycgi);
	}
	exit;
}

#-------------------------------------------------
#  NGスレッドワード設定
#-------------------------------------------------
sub set_ngthread_words {
	# 値をセット
	my $ngthread = NGThread->new();
	$ngthread->set_ng_thread_creator($in{'ng_thread_creator'});             # スレッド作成者のNG設定
	$ngthread->set_ng_thread_title($in{'ng_thread_title'});                 # スレッド名のNG設定
	$ngthread->set_ng_thread_title_exclude($in{'ng_thread_title_exclude'}); # スレッド名のNGの除外設定

	# Cookie保存
	$ngthread->save();

	# 完了画面表示
	success('NGスレッドワードに設定しました。', $historycgi);
	exit;
}

#-------------------------------------------------
#  書き込みスレッド履歴削除
#-------------------------------------------------
sub delete_post_history {
	# 書込IDを取得
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};
	if ($chistory_id eq '') {
		# 書込IDを取得できない時は書き込み履歴ページに強制移動
		print "Location: $historycgi\n\n";
		exit;
	}

	# 削除するスレッド番号が1つ以上ある時、書き込み履歴ログを開いて削除する
	my @delete_thread_no_array = map { int($_) } split("\0", $in{'thread_no'}); # 削除するスレッド番号を取得
	if (scalar(@delete_thread_no_array) > 0) {
		# HistoryLogインスタンスを初期化
		my $history_log = HistoryLog->new($chistory_id);

		# 書き込みスレッド履歴を削除
		$history_log->delete_post_histories(\@delete_thread_no_array);

		# HistoryLogインスタンス解放
		$history_log->DESTROY();
	}

	# 成功メッセージ表示
	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<p>スレッドを削除しました。</p>
<p>
<input type="button" value="前画面にもどる" onclick="location.href='$historycgi?edit=1'">
</div>
</body>
</html>
EOM
	exit;
}
