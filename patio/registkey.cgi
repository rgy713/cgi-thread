#!/usr/bin/perl

#┌─────────────────────────────
#│ ●投稿キー用画像表示モジュール
#│ registkey.cgi - 2007/02/25
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────

# 外部ファイル取り込み
require './init.cgi';

# GIF画像（変更不可）
%gif_img = (
	0 => {
		10 => "080012000002158c8fa9cb0b8fc09186068ba7aefbf63c41cd481e0500",
		12 => "0a00130000021a8c8fa9cbdd00560cf3548aaecedc76b37922984c97753a2a530000",
		},
	1 => {
		10 => "080012000002108c8fa9cb0c09e27a8ac2896b6ebc9f0200",
		12 => "0a0013000002158c8fa9cbedd0e00232c1aab08d9c69f41da1432a0500",
		},
	2 => {
		10 => "080012000002148c8fa9cb0b8fc09186061b15aebaeb0735e2681400",
		12 => "0a0013000002178c8fa9cbcd00153813557365cbf6f9c5511b443aa6590000",
		},
	3 => {
		10 => "080012000002158c8fa9cb0b8fc09186061b1374b3575f6dcd481a0500",
		12 => "0a0013000002178c8fa9cbcd001538135573e55bb1654d59222675ce791600",
		},
	4 => {
		10 => "080012000002148c8fa9cb0d0a5e8a33c8f3ae353a7ab868cd481600",
		12 => "0a0013000002188c8fa9cbed0118886b567829a2dae80e4da2d480db833a0500",
		},
	5 => {
		10 => "080012000002158c8fa9cb0aff0e58d3415443c6b29bbc5dcd481e0500",
		12 => "0a0013000002198c8fa9cbcd0061028d2e7b839c16e78778e2e1199183a6410100",
		},
	6 => {
		10 => "080012000002158c8fa9cb0c90609073bd87a83edbf4ca61cd481e0500",
		12 => "0c00130000021d8c8fa9cbed0e220387266b707d542eaf6d22a28541f9658df7b4ee510000",
		},
	7 => {
		10 => "080012000002108c8fa9cb0aff16908ed6342f6ebca70200",
		12 => "0a0013000002128c8fa9cbbd0063038cbe5971be9bbb0f060500",
		},
	8 => {
		10 => "080012000002168c8fa9cb0b8fc09186068b239cbcf6fb5d5b4396460100",
		12 => "0a00130000021a8c8fa9cbdd00560cf3548aeec53c41696c5a46965b783aea520000",
		},
	9 => {
		10 => "080012000002158c8fa9cb0b8fc09186068ba79ecfc6ed5d6143960500",
		12 => "0a00130000021a8c8fa9cbdd00560cf3548aaece6942f55d1d679158f739ea5a0000",
		},
	'w' => {
		10 => 8,
		12 => 12,
		},
	'h' => {
		10 => 18,
		12 => 19,
		},
	);

# 投稿キー文字数（変更不可）
$key_len = 4;

# パラメータ受け取り
$buf = $ENV{'QUERY_STRING'};
$buf =~ s/\%21/!/g;
$buf =~ s/<//g;
$buf =~ s/>//g;
$buf =~ s/"//g;
$buf =~ s/&//g;
$buf =~ s/\s//g;
$buf =~ s/\0//g;

# 画像表示
require $regkeypl;
&key_image;

#-------------------------------------------------
#  投稿キー画像
#-------------------------------------------------
sub key_image {
	# 復号
	local($plain) = &pcp_decode($buf, $pcp_passwd);

	# 先頭の４文字を抽出
	$plain =~ s/^(\d{$key_len}).*/$1/;

	# 画像１枚あたりサイズ
	local($gif_w, $gif_h);
	$gif_w = $gif_img{'w'}{$regkey_pt};
	$gif_h = $gif_img{'h'}{$regkey_pt};

	# 表示開始
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	print &gif_head;
	print &gif_body;
	print "\x3B";

	exit;
}

#-------------------------------------------------
# GIFヘッダ
#-------------------------------------------------
sub gif_head {
	# Signature(3B) 
	# Version(3B) 
	my $ret = "GIF89a";

	# Logical Screen Width(2B)
	$ret .= pack("C2", $gif_w*$key_len%256, ($gif_w*$key_len/256)%256);
	# Logical Screen Height(2B)
	$ret .= pack("C2", $gif_h%256, ($gif_h/256)%256);

	# GCTF(1b) CR(3b) SF(1b) SGCT(3b) 
	# Background Color Index(1B)
	# Pixel Aspect Ratio(1B)
	$ret .= pack("H*", "800000");

	# 文字色 : Global Color Table(0～255×3B)
	$moji_col =~ /^#?([a-f0-9]{6})$/i;
	$ret .= pack("H*", $1);

	# 背景色 : Global Color Table(0～255×3B)
	$back_col =~ /^#?([a-f0-9]{6})$/i;
	$ret .= pack("H*", $1);

	$ret;
}

#-------------------------------------------------
# GIF本体
#-------------------------------------------------
sub gif_body {
	my $ret;

	local($w) = 0;
	foreach ( split(//, $plain) ) {

		# Extension Introducer(1B) 
		# Graphic Control Label(1B) 
		# Block Size(1B)
		# R(3b) DM(3b) UIF(1b) TCF(1b) 
		# Delay Time(2B)
		# Transparent Color Index(1B)
		# Block Terminator(1B) 
		$ret .= pack("H*", "21f9040000000000");

		# Image Separator(1 Byte) 
		$ret .= "\x2C";

		# Logical Screen Width(2B)
		$ret .= pack("C2", $w%256, ($w/256)%256);
		$w += $gif_w;

		# Logical Screen Height(2B)
		$ret .= pack("C2", 256, 256);

		# 画像本体
		$ret .= pack("H*", $gif_img{$_}{$regkey_pt});
    	}
	$ret;
}

