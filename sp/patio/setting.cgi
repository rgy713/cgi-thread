#!/usr/bin/perl

# �ݒ���e�\���X�N���v�g�i�Ȃ��Ă��f���̓���ɂ͊֌W����܂���j

#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� setting.cgi - 2006/10/09
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���肵�܎� K0.973
# 2010/06/23 �V�K�X���b�h�쐬�ƃ��X�̃^�C�}�[�𕪂��Ă݂܂���
# 0.74 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V

# �O���t�@�C����荞��
require './init.cgi';
require $jcode;

$title = $title."�̐ݒ���e";

#-------------------------------------------------
#  ���j���[���\��
#-------------------------------------------------


	$hothour = int ($hot/3600);
	
	&header();
	print <<"EOM";
<div align="center">
<table width="95%"><tr><td align=right nowrap>
<a href="./patio.cgi">�g�b�v�y�[�W</a> &gt; <a href="./note.html">���ӎ���</a> &gt; �ݒ���e
</td></tr></table>
<Table border=0 cellspacing=0 cellpadding=0 width="95%">
<Tr bgcolor="#8080C0"><Td bgcolor="#8080C0">
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr bgcolor="#DCDCED"><td bgcolor="#DCDCED" nowrap width="92%">
<img src="./img/book.gif" align="absmiddle">
&nbsp; <b>�ݒ���e</b> $ver</td>
</tr></table></Td></Tr></Table>
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col1" colspan="3">
	<font color="$col2"><b>���̌f���̐ݒ���e</b></font>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap><b>����</b></td>
  <td bgcolor="$col2" nowrap><b>�ݒ�l</b></td>
  <td bgcolor="$col2" nowrap><b>���l</b></td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >1�X���b�h������̍ő�L����</td>
  <td bgcolor="$col2" nowrap>$m_max�R�����g</td>
  <td bgcolor="$col2" nowrap>���X����������z����Ɖߋ����O�Ɉڍs���܂�</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >���s���O�̃X���b�h��</td>
  <td bgcolor="$col2" nowrap>$i_max�X���b�h</td>
  <td bgcolor="$col2" nowrap>�X���b�h����������z����ƌÂ����ɉߋ����O�Ɉڍs���܂�</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�ߋ����O�̃X���b�h��</td>
  <td bgcolor="$col2" nowrap>$p_max�X���b�h</td>
  <td bgcolor="$col2" nowrap>�ߋ����O�̃X���b�h����������z����ƃX���b�h�͍폜����܂�</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�X���b�h�쐬�Ԋu</td>
  <td bgcolor="$col2" nowrap>$wait_thread�b</td>
  <td bgcolor="$col2" nowrap>�X���b�h�̍쐬�͂��̎��Ԉȏ�҂��Ă���s�Ȃ��ĉ����� 0=������</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >���X���e�Ԋu</td>
  <td bgcolor="$col2" nowrap>$wait_response�b</td>
  <td bgcolor="$col2" nowrap>���X�̓��e�͂��̎��Ԉȏ�҂��Ă���s�Ȃ��ĉ����� 0=������</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >���{��`�F�b�N</td>
  <td bgcolor="$col2" nowrap>$jp_wd</td>
  <td bgcolor="$col2" nowrap>�������݂ɓ��{�ꂪ�܂܂�邩���肵�܂� 0=���� 1=�L��</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >URL������</td>
  <td bgcolor="$col2" nowrap>$urlnum�܂�</td>
  <td bgcolor="$col2" nowrap>���e���Ɋ܂߂邱�Ƃ�������Ă���URL�̐� 0=������</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�R�����g���͕�����</td>
  <td bgcolor="$col2" nowrap>$max_msg����</td>
  <td bgcolor="$col2" nowrap>�S�p���Z</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�ő哊�e�\\�T�C�Y</td>
  <td bgcolor="$col2" nowrap>$maxdata�o�C�g</td>
  <td bgcolor="$col2" nowrap>�{���ƓY�t�t�@�C���̍��v</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >���e�L�[���e����</td>
  <td bgcolor="$col2" nowrap>$pcp_time��</td>
  <td bgcolor="$col2" nowrap>�t�H�[����\\�������Ă��瓊�e����܂ł̎��Ԑ���</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�V���\\������</td>
  <td bgcolor="$col2" nowrap>$hothour����</td>
  <td bgcolor="$col2" nowrap>�V���\\������鎞��</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�Ǘ��҂ɂ��p�X���[�h�N���A</td>
  <td bgcolor="$col2" nowrap>$clearpass</td>
  <td bgcolor="$col2" nowrap>�Ǘ��҂��ҏW�����ꍇ�A���[�U�[�̃p�X���[�h���N���A���邩 0=�ێ����� 1=�N���A����i���[�U�[���ҏW�ł��Ȃ��Ȃ�j</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >���X���m�点���[��</td>
  <td bgcolor="$col2" nowrap>$mailnotify</td>
  <td bgcolor="$col2" nowrap>���X���������Ƃ��Ƀ��[���ł��m�点 0=���Ȃ� 1=�X���b�h�𗧂Ă��l�̂� 2=�R�����g�����l���܂ߑS���j</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >�V�K�X���b�h�쐬����</td>
  <td bgcolor="$col2" nowrap>$createonlyadmin</td>
  <td bgcolor="$col2" nowrap> 0=�N�ł��쐬�ł��� 1=�Ǘ��҂̂݁i���[�U�[�̓X���b�h���쐬�ł��Ȃ��j</td>
</tr>
</table></Td></Tr></Table>
<br><br>
<!-- ���쌠�\\�����E�폜�֎~ ($ver) -->
<span class="s1">
- <a href="http://www.kent-web.com/" target="_top">Web Patio</a> -
 <a href="http://kirishima.cc/patio/" target="_top">���肵�܎�</a> -
</span></div>
</body>
</html>
EOM

