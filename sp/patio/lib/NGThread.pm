package NGThread;
use strict;
use JSON::XS;
use Encode qw();

use constant {
    DisplayMode_Hide => 0,
    DisplayMode_Replace => 1,
};

my @SETTINGS_KEYS = ('DisplayMode', 'ThreadCreator', 'ThreadTitle', 'ThreadTitleExclude');

# �G�X�P�[�v�����R���p�C���ςݐ��K�\����Ԃ�
my $regex_quote_compile = sub {
    my $quoted_word = quotemeta($_[0]);
    return qr/$quoted_word/;
};

my $IN_BRACKET_WORD_SEPARATER = '|';

my $AND_SEPARATE_REGEX = qr/_/;
my $META_SPLIT_REGEX = qr/(\[[^\[\]]*\])/;
my $BRACKET_CAPTURE_REGEX = qr/^\[([^\[\]]*)\]$/;
my $IN_BRACKET_WORD_SEPARATE_REGEX = $regex_quote_compile->($IN_BRACKET_WORD_SEPARATER);
my $LINE_BREAK_REGEX = qr/\r\n|\n|\r/;

my %compiled_regex_hash;

# �����񂪐ݒ�Ƀ}�b�`���邩�ǂ���
my $is_str_match_to_setting = sub {
    my ($str, $settings, $must_include_strings_array_ref) = @_;

    # �����G���R�[�h�ɕϊ�
    my $utf8flagged_str = $main::enc_cp932->decode($str);
    my $utf8flagged_settings = Encode::is_utf8($settings) ? $settings : $main::enc_cp932->decode($settings);

    # �����Ώە����񂩂�A�ݒ蕶����Ɋ܂ނׂ�������̃��X�g���쐬
    my @must_include_strings = do {
        my @tmp = ();
        if (defined($must_include_strings_array_ref) && ref($must_include_strings_array_ref) eq 'ARRAY') {
            foreach my $include_string (@{$must_include_strings_array_ref}) {
                my $utf8flagged_include_string = Encode::is_utf8($include_string) ? $include_string : $main::enc_cp932->decode($include_string);
                if (index($utf8flagged_str, $utf8flagged_include_string) >= 0) {
                    push(@tmp, $utf8flagged_include_string);
                }
            }
        }
        @tmp;
    };

    # �ݒ�1�s���ɔ���
    LINE_LOOP: foreach my $line (grep { $_ ne '' } split($LINE_BREAK_REGEX, $utf8flagged_settings)) {
        # �ݒ蕶����Ɋ܂ނׂ��������S�Ċ܂܂�Ă��邩�ǂ����`�F�b�N
        if (grep { index($line, $_) == -1 } @must_include_strings) {
            next; # �܂܂�Ă��Ȃ�������1�ȏ㌩���������́ANG�������Ȃ����߃X�L�b�v
        }

        # AND�����u_�v����
        my @and_set;
        push(@and_set, grep { $_ ne '' } split($AND_SEPARATE_REGEX, $line));

        # ��������̓X�L�b�v
        if (scalar(@and_set) == 0) {
            next;
        }

        # �d���������J�E���g���A���j�[�N������
        my %exp_count;
        @and_set = grep(!$exp_count{$_}++, @and_set);

        # ���K�\���ɂ�锻����s�����ǂ��� (�d�����������邩�A�������́A���^�������܂�ł��邩)
        if (scalar(grep { $_ > 1 } values(%exp_count)) || scalar(grep { $_ =~ $META_SPLIT_REGEX } @and_set) > 0) {
            # ���K�\���ɂ�镔����v����
            # AND�������Ƃɔ�����{
            foreach my $and_keyword (@and_set) {
                # ���K�\�����܂��R���p�C�����Ă��Ȃ������̏ꍇ�̓p�^�[�����쐬���āA�R���p�C�����s��
                if (!exists($compiled_regex_hash{$and_keyword}) || !exists($compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}})) {
                    my $regex_str = '';
                    # ���^����([])�ŕ���
                    foreach my $meta_splited_keyword (grep { $_ ne '' } split($META_SPLIT_REGEX, $and_keyword)) {
                        if ($meta_splited_keyword =~ $BRACKET_CAPTURE_REGEX) {
                            # []�̃}�b�`
                            # ������v����̂��߁A�����N���X���K�\�����쐬���ăn�b�V���Ɋi�[
                            if (index($1, $IN_BRACKET_WORD_SEPARATER) == -1) {
                                # ������v����̂��߁A�����N���X���K�\�����쐬���ăn�b�V���Ɋi�[
                                # ���K�\�����g�p���邽�߁A�e�������G�X�P�[�v
                                $regex_str .= '[' . quotemeta($1) . ']';
                            } else {
                                # |�ɂ��P�ꕪ��OR����
                                my @word_or_regex_str_array;
                                foreach my $word (grep { $_ ne '' } split($IN_BRACKET_WORD_SEPARATE_REGEX, $1)) {
                                    push(@word_or_regex_str_array, quotemeta($word)); # ���K�\�����g�p���邽�߁A�e�������G�X�P�[�v
                                }
                                $regex_str .= '(?:' . join('|', @word_or_regex_str_array) . ')'; # �p�^�[���𐶐�
                            }
                        } else {
                            # ����ȊO�̒ʏ핶����
                            $regex_str .= quotemeta($meta_splited_keyword);
                        }
                    }
                    if ($regex_str ne '') {
                        # �����o���񐔂ɂ���č쐬���鐳�K�\����ς���
                        if ($exp_count{$and_keyword} == 1) {
                            $compiled_regex_hash{$and_keyword}{1} = qr/$regex_str/;
                        } else {
                            # �����ɏo���񐔎w��(n��ȏ�)�����邽�߁A����������Đ��K�\�����쐬
                            $compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}} = qr/(?:.*?$regex_str.*?){$exp_count{$and_keyword},}/;
                        }
                    } else {
                        $compiled_regex_hash{$and_keyword} = undef;
                    }
                }

                # ������{
                if ($utf8flagged_str !~ $compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}}) {
                    # �s��v���͎��̐ݒ�s�����
                    next LINE_LOOP;
                }
            }
            # �ݒ�s�̂��ׂĂɍ��v����
            return 1;
        } else {
            # �ʏ�̕�����v�ɂ�锻��
            # AND�������Ƃɔ�����{
            foreach my $and_keyword (@and_set) {
                if (index($utf8flagged_str, $and_keyword) == -1) {
                    # �s��v���͎��̐ݒ�s�����
                    next LINE_LOOP;
                }
            }
            # �ݒ�s�̂��ׂĂɍ��v����
            return 1;
        }
    }

    # ������̐ݒ�s�ɂ���v���Ȃ�����
    return 0;
};

sub new {
    my ($class, $history_log) = @_;
    my $self = {};

    # �ݒ�ǂݍ���
    my $load_values;
    if (defined($history_log)) {
        $self->{HISTORY_LOG} = $history_log;
        # ����ID���O����ݒ�ǂݍ���
        $load_values = $history_log->get_ngthread_settings();
    } else {
        # Cookie����ݒ�ǂݍ���
        $self->{NAME} = "WEB_PATIO_${main::cookie_current_dirpath}_NGThread";
        foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
            my ($key, $value) = split(/=/, $cookie_set);
            if ($key eq $self->{'NAME'}) {
                if ($value ne '') {
                    my $urldecoded_value = $value;
                    $urldecoded_value =~ s/\+/ /g;
                    $urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack("H2",$1)/eg;
                    $urldecoded_value = Encode::decode('UTF-8', $urldecoded_value);
                    $load_values = JSON::XS->new()->utf8(0)->decode($urldecoded_value);
                }
                last;
            }
        }
    }
    if (defined($load_values)) {
        # �ǂݍ��񂾐ݒ�l����`����Ă��鎞�A
        # �K�v�ɉ����ē����G���R�[�h��CP932�ɕϊ����A
        # �ݒ�l�Ƃ��Ďg�p����
        foreach my $setting_key (@SETTINGS_KEYS) {
            if (exists(${$load_values}{$setting_key}) && ${$load_values}{$setting_key} ne '') {
                if (Encode::is_utf8(${$load_values}{$setting_key})) {
                    $self->{$setting_key} = $main::enc_cp932->encode(${$load_values}{$setting_key});
                } else {
                    $self->{$setting_key} = ${$load_values}{$setting_key};
                }
            }
        }
        $self = { %{$load_values}, %{$self} };
    }

    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        my $field = shift;
        if (@_) {
            $self->{$field} = shift;
        }
        if (exists($self->{$field})) {
            return $self->{$field};
        } else {
            return;
        }
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $history_log = $self->('HISTORY_LOG'))) {
        $history_log->DESTROY();
    }
}

sub get_display_mode {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('DisplayMode'))) {
        if ($self->('DisplayMode') >= 0) {
            return $self->('DisplayMode');
        } else {
            # 0�������Z�b�g����Ă��鎞�̓f�t�H���g�l���g�p����
            return $main::ngthread_default_display_mode;
        }
    } else {
        return $main::ngthread_default_display_mode;
    }
}

sub set_display_mode {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if ($value != DisplayMode_Hide && $value != DisplayMode_Replace) {
        confess('setting display mode is not valid.');
    }

    $self->('DisplayMode', int($value));
}

sub get_ng_thread_creator {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadCreator'))) {
        return $self->('ThreadCreator');
    } else {
        return '';
    }
}

sub set_ng_thread_creator {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadCreator', $value);
}

sub get_ng_thread_title {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadTitle'))) {
        return $self->('ThreadTitle');
    } else {
        return '';
    }
}

sub set_ng_thread_title {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadTitle', $value);
}

sub get_ng_thread_title_exclude {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadTitleExclude'))) {
        return $self->('ThreadTitleExclude');
    } else {
        return '';
    }
}

sub set_ng_thread_title_exclude {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadTitleExclude', $value);
}

sub is_ng_thread_creator {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (!defined($self->('ThreadCreator'))) {
        return 0;
    }

    return $is_str_match_to_setting->($value, $self->get_ng_thread_creator(), \@main::ngthread_thread_creator_must_include_strings);
}

sub is_ng_thread_title {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (!defined($self->('ThreadTitle'))) {
        return 0;
    }

    return $is_str_match_to_setting->($value, $self->get_ng_thread_title())
        && !$is_str_match_to_setting->($value, $self->get_ng_thread_title_exclude());
}

sub save {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    my %save_values;
    foreach my $key (@SETTINGS_KEYS) {
        if (defined($self->($key)) && $self->($key) ne '') {
            if ($key eq 'DisplayMode') {
                $save_values{$key} = int($self->($key));
            } else {
                $save_values{$key} = $main::enc_cp932->decode($self->($key));
            }
        }
    }
    if (!defined($self->('DisplayMode'))) {
        # DisplayMode�̐ݒ肪�Ȃ��ꍇ�ł��A�̈���m�ۂ��ăf�t�H���g�l�ł��邱�Ƃ��L�^����
        # (��ɋK��o�C�g�����߂Őݒ�ł��Ȃ��Ȃ��Ă��܂����Ƃ�h������)
        $save_values{'DisplayMode'} = -1;
    }

    if (defined(my $history_log = $self->('HISTORY_LOG'))) {
        # ����ID���O�t�@�C���ɕۑ�
        $history_log->set_ngthread_settings(\%save_values);
    } else {
        # Cookie�ۑ��̂��߁AJSON�ɂ���URL�G���R�[�h
        my $urlencoded_json_settings = JSON::XS->new->utf8(1)->encode(\%save_values);
        $urlencoded_json_settings =~ s/(\W)/'%' . unpack('H2', $1)/eg;
        $urlencoded_json_settings =~ s/\s/+/g;

        # Cookie�T�C�Y����E�Z�b�g
        if(length($self->('NAME') . $urlencoded_json_settings) > 4093) {
            main::error('�������I�[�o�[�ł��B', $main::bbscgi);
        } else {
            print 'Set-Cookie: ' . $self->('NAME') . "=$urlencoded_json_settings; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
        }
    }
}

1;

=pod

=encoding cp932

=head1 NAME
NGThread - WebPatio NG�X���b�h���W���[��

=head1 SYNOPSIS
use NGThread;

# ����ID���O����ݒ�̓ǂݍ���
# (�����ɗ^����$history_log��HistoryLog���W���[���̃C���X�^���X)
$ngthread = NGThread->new($history_log);

# Cookie����ݒ�̓ǂݍ���
$ngthread = NGThread->new();

# NG�X���b�h�\���ݒ�̎擾
$ngthread->get_display_mode();

# NG�X���b�h�\���ݒ�̃Z�b�g
$ngthread->set_display_mode(NGThread::DisplayMode_Hide);    # �X���b�h��\���ɃZ�b�g
$ngthread->set_display_mode(NGThread::DisplayMode_Replace); # �X���b�h���u���ɃZ�b�g

# �X���b�h�쐬�҂�NG�ݒ���擾
my $value = $ngthread->get_ng_thread_creator();

# �X���b�h�쐬�҂�NG�ݒ���Z�b�g
$ngthread->set_ng_thread_creator($value);

# �X���b�h����NG�ݒ���擾
my $value = $ngthread->get_ng_thread_title();

# �X���b�h����NG�ݒ���Z�b�g
$ngthread->set_ng_thread_title($value);

# �X���b�h����NG�̏��O�ݒ���擾
my $value = $ngthread->get_ng_thread_title_exclude();

# �X���b�h����NG�̏��O�ݒ���Z�b�g
$ngthread->set_ng_thread_title_exclude($value);

# �X���b�h�쐬�҂�NG�ݒ�Ɉ�v���邩�ǂ���
if ($ngthread->is_ng_thread_creator($thread_creator)) {
    # ��v����ꍇ�̏���
}

# �X���b�h����NG�ݒ�Ɉ�v���邩�ǂ���
if ($ngthread->is_ng_thread_title($thread_title)) {
    # ��v����ꍇ�̏���
}

# �ݒ�ς݂�NG�X���b�h�ݒ������ID���O/Cookie�ɕۑ�
$ngthread->save();

=head1 INTERFACE

=head2 Package Constants

=over

=item DisplayMode_Hide NG�X���b�h�\���ݒ� �X���b�h��\��

=item DisplayMode_Replace NG�X���b�h�\���ݒ� �X���b�h���u��

=back

1;
