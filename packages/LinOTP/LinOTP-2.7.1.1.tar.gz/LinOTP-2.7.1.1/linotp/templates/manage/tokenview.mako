# -*- coding: utf-8 -*-    
<!--
 *
 *   LinOTP - the open source solution for two factor authentication
 *   Copyright (C) 2010 - 2014 LSE Leading Security Experts GmbH
 *
 *   This file is part of LinOTP server.
 *
 *   This program is free software: you can redistribute it and/or
 *   modify it under the terms of the GNU Affero General Public
 *   License, version 3, as published by the Free Software Foundation.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the
 *              GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *
 *    E-mail: linotp@lsexperts.de
 *    Contact: www.linotp.org
 *    Support: www.lsexperts.de
 *
-->
 <button class='ui-button' id='button_losttoken'>${_("Lost token")}</button>
 <button class='ui-button' id='button_tokeninfo'>${_("Token info")}</button>
 <button class='ui-button' id='button_resync'>${_("Resync Token")}</button>
 <button class='ui-button' id='button_tokenrealm'>${_("set token realm")}</button>
 <button class='ui-button' id='button_getmulti'>${_("get OTP")}</button>
 
<table id="token_table" class="flexme2" style="display:none"></table>
   
<script type="text/javascript"> 
view_token();
tokenbuttons();
</script>


