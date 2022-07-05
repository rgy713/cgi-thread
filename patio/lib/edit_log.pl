#┌─────────────────────────────────
#│ [ WebPatio ]
#│ edit_log.pl - 2007/06/06
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# 2009/12/07 ログの編集結果をメールするルーチンに $mailing のオプションを適用するように
# 2009/07/06 ログを削除したときにカウントし直すロジック変更
#            ログをユーザーが編集したとき、そのタイムスタンプをスレッド一覧のタイムスタンプにするように変更
# 2009/06/26 ログを編集する際、個別ログの$keyで上書きしてindexを更新するのに、変数に格納していたので捨てるようにした
#            ログ編集後、管理モードの続行と、管理モードの終了が選べるようにした
# 2009/06/15 ログを編集する際、レス数をカウントし直すロジックを間違えていたので修正
# 2009/05/29 ユーザー間メール送信を利用しない設定のときにアイコンを非表示に
# 2007/01/09 管理者ロック時、管理者は編集できるように調整
# 2007/12/17 管理者による編集時に、パスワードを消すかどうかオプションで指定できるようにした。
# 2007/09/30 記事編集時、メールアドレス入力の制御をしているのに対応していなかった点を修正
# 2007/06/13 管理者による編集時には、書き込みのパスワードを消すように。編集内容を元に戻すユーザーがいたため。
# 2007/06/10 3.2相当に修正
# 2007/05/01 親記事を修正すると名前が消えるバグ修正
# 2007/05/01 3.13に対応
#            ログをエディターで直接編集することを想定して、記事編集時には、レスの数をカウントし直すように
# きりしまによる改造版 2007.04.06

use List::Util qw/max/;

#-------------------------------------------------
#  記事修正
#-------------------------------------------------
sub edit_log {
	local $j;
	local($myjob) = @_;

	if ($myjob eq "admin") {
		$in{'f'}  = $in{'no'};
		$in{'no'} = $in{'no2'};
	}
	local($mylog,$idxfile);
	if ($in{'bakfile'}) {
		$idxfile = $pastfile;
		$mylog = 'bakfile';
	} else {
		$idxfile = $nowfile;
		$mylog = 'logfile';
	}

	# 汚染チェック
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# スレッドログファイルパス取得
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";

	# 添付ファイル最大数
	my $max_upl_num = 3 + $upl_increase_num;

	# 修正処理
	if ($in{'job'} eq "edit2") {

		# 管理者オペ
		if ($in{'pass'} ne "") {
			$admin_flag = 1;
			if ($in{'pass'} ne $pass) { &error("パスワードが違います"); }
		# ユーザー画面から管理パスを入力
		} elsif ($in{'pwd'} eq $pass) {
			$admin_flag = 1;

		# ユーザオペ
		} elsif ($in{'pwd'} ne "") {
			$admin_flag = 0;

			# チェック
			if ($no_wd) { &no_wd; }
			if ($jp_wd) { &jp_wd; }
			if ($urlnum > 0) { &urlnum; }

		# オペ不明
		} else {
			&error("不正なアクセスです");
		}

		# 投稿内容チェック
		if ($i_com eq "") { &error("コメントの内容がありません"); }
		if ($i_nam eq "") {
			if ($in_name) { &error("名前は記入必須です"); }
			else { $i_nam = '名無し'; }
		}
#		if ($in_mail && $in{'email'} eq "") { &error("E-mailは記入必須です"); }
	if ($in_mail == 1 && $in{'email'} eq "") { &error("E-mailは記入必須です"); }
	if ($in_mail == 2 && $in{'email'} ne "") { &error("E-mailは入力禁止です"); }
	if ($in_mail == 3 && $in{'email'} ne "") { &error("E-mailは入力禁止です"); }
		if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/)
			{ &error("E-mailの入力内容が不正です"); }
		if ($i_sub eq "")
			{ &error("タイトルは記入必須です"); }
		if ($i_sub =~ /^(\x81\x40|\s)+$/)
			{ &error("タイトルは正しく記入してください"); }
		if ($i_nam =~ /^(\x81\x40|\s)+$/)
			{ &error("名前は正しく記入してください"); }
		if ($i_com =~ /^(\x81\x40|\s|<br>)+$/)
			{ &error("コメントは正しく記入してください"); }
		if ($in{'url'} eq "http://") { $in{'url'} = ""; }

		local($top, $new_log);
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";
		$top = <DAT>;
#		$j = -1;
		# ヘッダ
		my ($num,$sub2,$res,$key) = split(/<>/, $top);
        my $last_log;
        my $res_cnt = 0; # 最終レス情報決定用レス数カウンタ (ログに記録するレス数は$resをそのまま使用)
		while(<DAT>) {
			local $idcrypt;
			my ($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl1,$upl2,$upl3,$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl4,$upl5,$upl6);

			$_ =~ s/(?:\r\n|\r|\n)$//;
			($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl1,$upl2,$upl3,$idcrypt,$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl4,$upl5,$upl6) = split(/<>/, $_);

			if ($tim eq "") { &error("この記事はアップロードできません"); }

			if ($in{'no'} == $no) {
				# パスチェック
				if (!$admin_flag) {
					if (!&decrypt($in{'pwd'}, $pw)) {
						&error("パスワードが違います");
					}
				}

				# トリップ
				unless ($i_nam =~ /◆/ && $i_nam eq $nam) {
					$i_nam = &trip($i_nam);
				}

				# 画像情報を取得
				my (%fn, %ex, %w, %h, %thumb_w, %thumb_h, %image_orig_md5, %image_conv_md5);
				my @upls = ($upl1, $upl2, $upl3, $upl4, $upl5, $upl6);
				foreach my $i (1 .. 6) {
					($fn{$i}, $ex{$i}, $w{$i}, $h{$i},
						$thumb_w{$i}, $thumb_h{$i}, $image_orig_md5{$i}, $image_conv_md5{$i}) = split(/,/, $upls[$i - 1]);

					# 添付削除
					if ($in{"del$i"} || $image_upl && $i <= $max_upl_num && $in{"upfile$i"}) {
						unlink("$upldir/$fn{$i}/$tim-$i$ex{$i}");
						unlink("$thumbdir/$fn{$i}/$tim-${i}_s.jpg");

						($fn{$i}, $ex{$i}, $w{$i}, $h{$i},
							$thumb_w{$i}, $thumb_h{$i}, $image_orig_md5{$i}, $image_conv_md5{$i}) = ();
					}
				}

				# 添付アップ
				if ($image_upl && grep { $in{'upfile' . $_} } (1 .. $max_upl_num)) {
					require $upload;
					my (%tmp_fn, %tmp_ex, %tmp_w, %tmp_h, %tmp_thumb_w, %tmp_thumb_h, %tmp_image_orig_md5, %tmp_image_conv_md5);
					($tmp_fn{1},$tmp_ex{1},$tmp_w{1},$tmp_h{1},$tmp_thumb_w{1},$tmp_thumb_h{1},$tmp_image_orig_md5{1},$tmp_image_conv_md5{1},
						$tmp_fn{2},$tmp_ex{2},$tmp_w{2},$tmp_h{2},$tmp_thumb_w{2},$tmp_thumb_h{2},$tmp_image_orig_md5{2},$tmp_image_conv_md5{2},
						$tmp_fn{3},$tmp_ex{3},$tmp_w{3},$tmp_h{3},$tmp_thumb_w{3},$tmp_thumb_h{3},$tmp_image_orig_md5{3},$tmp_image_conv_md5{3},
						$tmp_fn{4},$tmp_ex{4},$tmp_w{4},$tmp_h{4},$tmp_thumb_w{4},$tmp_thumb_h{4},$tmp_image_orig_md5{4},$tmp_image_conv_md5{4},
						$tmp_fn{5},$tmp_ex{5},$tmp_w{5},$tmp_h{5},$tmp_thumb_w{5},$tmp_thumb_h{5},$tmp_image_orig_md5{5},$tmp_image_conv_md5{5},
						$tmp_fn{6},$tmp_ex{6},$tmp_w{6},$tmp_h{6},$tmp_thumb_w{6},$tmp_thumb_h{6},$tmp_image_orig_md5{6},$tmp_image_conv_md5{6}) = &upload($tim, $in{'increase_num'}, 1);

					foreach my $i (1 .. $max_upl_num) {
						if (!$tmp_ex{$i}) {
							next;
						}
						($fn{$i},$ex{$i},$w{$i},$h{$i},$thumb_w{$i},$thumb_h{$i},$image_orig_md5{$i},$image_conv_md5{$i})
							= ($tmp_fn{$i},$tmp_ex{$i},$tmp_w{$i},$tmp_h{$i},$tmp_thumb_w{$i},$tmp_thumb_h{$i},$tmp_image_orig_md5{$i},$tmp_image_conv_md5{$i});
					}
				}

				# レス情報を更新
				if ($admin_flag) {
					# 管理者の編集は記録日時を維持する
					$time = $tim;
					$date = $dat;

					# パスワードクリアフラグが立っている場合は、パスワードを空欄にする
					if ($in{'clearpass'}) {
						$pw = '';
					}
				} else {
					# 管理者以外の編集は記録日時を現在日時に更新
					# ($timを更新してしまうと、添付ファイルアクセスに支障が出るためそのままとする)
					$dat = $date;

					# 管理者以外の編集ではIDを作成しなおす
					if($idkey) { &makeid; }
					else { $idcrypt = "";}
				}

				# 更新するログ行を作成
				$_ = join('<>',
					$no,
					$in{'sub'},
					$i_nam,
					$in{'email'},
					$in{'comment'},
					$dat,
					$host,
					$pw,
					$in{'url'},
					$in{'mvw'},
					$myid,
					$tim,
					"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
					"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
					"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
					$idcrypt,
					$user_id,
					$is_sage,
					$cookie_a,
					$history_id,
					$log_useragent,
					$is_private_browsing_mode,
					$first_access_datetime,
					"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
					"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
					"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
					'' # 改行のためのダミー要素
				);
			}
			$new_log .= "$_\n";
			$last_log = $_;
			$res_cnt++;
#			$j++;
		}

		# 親記事の場合は題名を更新
		if ($in{'no'} == 1) { $sub2 = $in{'sub'}; }

		seek(DAT, 0, 0);
		print DAT "$num<>$sub2<>$res<>$key<>\n" . $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 最終投稿者名
#		($last_nam) = (split(/<>/, $new[$#new]))[2];
		# と時間・タイトルも取得
		($last_sub,$last_nam,$last_dat) = (split(/<>/, $last_log))[1,2,5];

		$res_cnt--; # レスカウントから親レスを除く
		if ($res_cnt == 0) {
			# 最終的にレスがない場合
#			$last_nam = "";
#			$last_dat = "";
			$last_sub = "";
#			$last_tim = "";
		}

		# index展開
		my $data;
		open(DAT,"+< $idxfile") || &error("Open Error: $idxfile");
		eval "flock(DAT, 2);";
		$top = <DAT> if (!$in{'bakfile'});
		while(<DAT>) {
			chomp($_);
#			local($no,$sub,$res,$nam,$da,$na2,$key2,$upl,$ressub,$restime) = split(/<>/);
			local($no,$sub,$re,$nam,$da,$na2,undef,$upl,$ressub,$restime) = split(/<>/);
			chomp ($ressub);
			chomp ($restime);

			if ($in{'f'} == $no) {
				if (!$admin_flag ) {
					$restime=$time;
				}
				# 親記事修正のとき
				if ($in{'no'} == 1) {

					# 親ログ
					local($tim,$upl1,$upl2,$upl3,$upl4,$upl5,$upl6) = (split(/<>/, $new[1]))[11 .. 14, 23 .. 25];
					my $ex1 = (split(/,/, $upl1))[1];
					my $ex2 = (split(/,/, $upl2))[1];
					my $ex3 = (split(/,/, $upl3))[1];
					my $ex4 = (split(/,/, $upl4))[1];
					my $ex5 = (split(/,/, $upl5))[1];
					my $ex6 = (split(/,/, $upl6))[1];
					if ($ex1 || $ex2 || $ex3 || $ex4 || $ex5 || $ex6) { $upl = $tim; } else { $upl = ''; }

#					if ($res2 == 0) { $na2 = $i_nam; }
#					if ($j < 1) { $last_sub = ""; }
					$_ = "$no<>$in{'sub'}<>$res<>$i_nam<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$restime<>";

				# レス記事修正のとき
				} else {
					$_ = "$no<>$sub<>$res<>$nam<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$restime<>";
				}
			}
			$data .= "$_\n";
		}

		# index更新
		$data = $top . $data if (!$in{'bakfile'});
		seek(DAT, 0, 0);
		print DAT $data;
		truncate(DAT, tell(DAT));
		close(DAT);

# 編集結果送信 *臨時措置
if ($mailing!=0) {
	# メールタイトルを定義
	$msub = "$title： \[$no\] $sub";

	# 本文の改行・タグを復元
	$mcom = $in{'comment'};
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/＜/g;
	$mcom =~ s/&gt;/＞/g;
	$mcom =~ s/&quot;/”/g;
	$mcom =~ s/&amp;/＆/g;

$mbody = <<EOM;
--------------------------------------------------------
$titleの記事が編集されました。

投稿日時：$dat
ホスト名：$host
ブラウザ：$ENV{'HTTP_USER_AGENT'}

おなまえ：$i_nam2
Ｅメール：$in{'email'}
タイトル：$in{'sub'}
ＵＲＬ  ：$in{'url'}

$mcom
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

		# 完了メッセージ
		&header;
		print "<blockquote>\n";
		print "<b>修正を完了しました</b><br>\n";

		# 管理モード
		if ($myjob eq "admin" || $in{'myjob'} eq "admin") {
		print "管理モード続行\n";
		print "<table><tr><td valign=top>\n";
			print "<form action=\"$admincgi\" method=\"post\">\n";
			print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
			print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
			print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
			print "<input type=\"submit\" value=\"スレッド一覧へ戻る\"></form>\n";

		print "</td><td width=15></td>\n";
		print "<td valign=top>\n";

			print "<form action=\"$admincgi\" method=\"post\">\n";
			print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
			print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
			print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
			print "<input type=\"hidden\" name=\"action\" value=\"view\">\n";
			print "<input type=\"hidden\" name=\"no\" value=\"$in{'f'}\">\n";
			print "<input type=\"submit\" value=\"個別メンテへ戻る\"></form>\n";
		print "</td></tr></table>\n";

		print "管理モード終了\n";

		}
		# 一般モード
#		} else {

		print "<table><tr><td valign=top>\n";

			print "<form action=\"$bbscgi\">\n";
			print "<input type=\"submit\" value=\"掲示板へ戻る\"></form>\n";
#		}

		# スレッドに戻る
		print "</td><td width=15></td>\n";
		print "<td valign=top>\n";
		# 一般モード
#		} else {
			print "<form action=\"$readcgi\">\n";
			print "<input type=\"hidden\" name=\"no\" value=\"$in{'f'}\">\n";
			print "<input type=\"submit\" value=\"スレッドへ戻る\"></form>\n";
#		}

		print "</td></tr></table>\n";

		print "</blockquote></body></html>\n";
		exit;
	}

	# 該当ログチェック
	local($flg, $top);
	open(IN, $logfile_path);
	$top = <IN>;
	while (<IN>) {
		$_ =~ s/(?:\r\n|\r|\n)$//;
		($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$user_id,$is_sage,$cookie_a,$history_id,
			$upl{4},$upl{5},$upl{6}) = (split(/<>/))[0 .. 14, 16 .. 19, 23 .. 25];

		last if ($in{'no'} == $no);
	}
	close(IN);

	# 管理者ロック時はユーザーは編集不可
	local(undef,undef,undef,$key) = split(/<>/, $top);
	if ($in{'pass'} ne $pass && $in{'pwd'} ne $pass && $key == 4) {
			&error("管理者ロックされている記事は編集できません");
	}
	if ($myjob eq "user" && $in{'pwd'} ne $pass) {
		if ($pw eq "") {
			if ($clearpass == 1) {
			&error("該当記事はパスワードが設定されていません。また、管理者により編集された場合も編集できなくなる設定になっています。");
			} else {
			&error("該当記事はパスワードが設定されていません");
			}
		}
		if (!&decrypt($in{'pwd'}, $pw)) { &error("パスワードが違います"); }
	}
#	  elsif ($in{'pwd'} eq $pass) {
#		$myjob eq "admin";
#	}

	if ($smile) { &header("", "js"); }
	else { &header(); }

	print <<"EOM";
<div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/mente.gif" align="top">
&nbsp; <b>記事修正フォーム</b></td>
<td align="right" bgcolor="$col3" nowrap>
<a href="javascript:history.back()">前画面に戻る</a></td>
</tr></table></Td></Tr></Table>
<p>
EOM

	if ($image_upl) {
		print qq|<form action="$registcgi" method="post" name="myFORM" enctype="multipart/form-data">\n|;
	} else {
		print qq|<form action="$registcgi" method="post" name="myFORM">\n|;
	}

	print <<EOM;
<input type="hidden" name="mode" value="edit_log">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="f" value="$in{'f'}">
<input type="hidden" name="no" value="$in{'no'}">
<input type="hidden" name="myjob" value="$myjob">
<input type="hidden" name="$mylog" value="1">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>題名</td>
  <td>
    <input type="text" name="sub" size="$sublength" value="$sub" maxlength="$sublength">
EOM
	print "    <input type=\"checkbox\" ";
	if ($is_sage eq '1') { print 'checked '; }
	print "disabled>sage\n";
	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>名前</td>
  <td><input type="text" name="name" size="30" value="$nam" maxlength="20"></td>
</tr>
EOM
	if ($user_id ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>登録ID</td>
  <td><input type="text" size="30" value="$user_id" disabled></td>
</tr>
EOM
	}
	if ($history_id ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>書込ID</td>
  <td><input type="text" size="30" value="$history_id" disabled></td>
</tr>
EOM
	}
	if ($cookie_a ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>CookieA</td>
  <td><input type="text" size="30" value="$cookie_a" disabled></td>
</tr>
EOM
	}
	if ($in_mail == 2) {
	} else {

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>E-Mail</td>
  <td><input type="text" name="email" size="30" value="$eml">
EOM

	if ($show_mail) {
		print "  <select name=\"mvw\">\n";
		if ($cmvw eq "") { $cmvw = 0; }
	@mvw = ('非表示','表示');
	foreach (0,1) {
		if ($mvw == $_) {
			print "<option value=\"$_\" selected>$mvw[$_]\n";
		} else {
			print "<option value=\"$_\">$mvw[$_]\n";
		}
	}
		print "</select>\n";
	} elsif ($usermail) {
		print "  <input type=\"hidden\" name=\"mvw\" value=\"0\"> 入力すると <img src=\"$imgurl/mail.gif\" alt=\"メールを送信する\" width=\"16\" height=\"13\" border=\"0\"> からメールを受け取れます（アドレス非表\示）\n";
	}
	if ($in_mail == 3) {
		print " 迷惑投稿防止のため何か入れると投稿できません\n";

	} elsif ($in_mail == 1) {
	print " （必須）\n";
	}
	print <<EOM;
</td>
</tr>
EOM

	}
	if ($url eq "") { $url = "http://"; }

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80">URL</td>
  <td bgcolor="$col2"><input type="text" name="url" size="45" value="$url"></td>
</tr>
EOM

	# 添付フォーム
	if ($image_upl) {
		print "<tr bgcolor=\"$col2\"><td bgcolor=\"$col2\" width=\"80\">添付</td>";
		print "<td bgcolor=\"$col2\">\n";
		print "<input type=\"hidden\" name=\"increase_num\" value=\"1\">\n";

		my $max_num = $max_upl_num;
		my @imgs = (undef);
		foreach my $i (1 .. 6) {
			my @img = split(/,/, $upl{$i});
			push(@imgs, \@img);
			if ($i > $max_num && $img[0] ne '') {
				$max_num = $i;
			}
		}

		foreach my $i (1 .. $max_num) {
			print "<input type=\"file\" name=\"upfile$i\" size=\"45\"";
			if ($i > $max_upl_num) {
				print " disabled";
			}
			print ">\n";

			my ($img_folder_number, $ex) = @{$imgs[$i]};
			if ($ex) {
				print "&nbsp;[<a href=\"$upldir/$img_folder_number/$tim-$i$ex\" target=\"_blank\">添付$i</a>]\n";
				print "<input type=\"checkbox\" name=\"del$i\" value=\"1\">添付削除\n";
			}
			print "<br>\n";
		}

		print "</td></tr>\n";
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80">コメント</td>
  <td bgcolor="$col2">
EOM

	# アイコン
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
		foreach (0 .. $#s1) {
			print "<a href=\"javascript:MyFace('$s2[$_]')\">";
			print "<img src=\"$imgurl/$s1[$_]\" border=0></a>\n";
		}
		print "<br>\n";
	}

	if ($myjob eq "admin") {
		print "<input type=hidden name=pass value=\"$in{'pass'}\">\n";
	} else {
		print "<input type=hidden name=pwd value=\"$in{'pwd'}\">\n";
	}

	$com =~ s/<br>/\n/g;
	print <<"EOM";
<textarea name="comment" cols="$cols" rows="$rows" wrap="soft">$com</textarea></td></tr>
EOM

if ($pw eq "") {
	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    この記事にはパスワードは設定されていません</td>
</tr>
EOM

} elsif ($myjob eq "admin" && $clearpass || $myjob eq "user" && $in{'pwd'} eq $pass && $clearpass ) {
	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="checkbox" name="clearpass" value="1" checked>記事のパスワードをクリアする</td>
</tr>
EOM
	}

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="submit" value="記事を修正する"></td>
  </form></tr></table>
</Td></Tr></Table>
</form></div>
</body>
</html>
EOM
	exit;
}



1;

