/*
 * Copyright 2020 by Aditya Mehra <aix.m@outlook.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import QtQuick.Layouts 1.4
import QtQuick 2.9
import QtQuick.Controls 2.2
import org.kde.kirigami 2.8 as Kirigami
import Mycroft 1.0 as Mycroft

Item {
    property string accountType: "General"
    
    ButtonGroup {
        buttons: row.children
    }
    
    onFocusChanged: {
        if(focus) {
            genButton.forceActiveFocus()
        }
    }
    
    Row {
    id: row
    anchors.fill: parent

        Label {
            text: "Account Type"
            color: Kirigami.Theme.textColor
            verticalAlignment: Text.AlignVCenter
            height: parent.height
        }
    
        RadioButton {
            id: genButton
            checked: true
            text: "General"
            KeyNavigation.right: sipComButton
            KeyNavigation.down: userNameFieldBox
            
            onCheckedChanged: {
                if(checked){
                    accountType = "General"
                }
            }
            
            Keys.onReturnPressed: {
                genButton.checked = true
            }
        }

        RadioButton {
            id: sipComButton
            text: "SipXCom"
            KeyNavigation.left: genButton
            KeyNavigation.down: userNameFieldBox
            
            onCheckedChanged: {
                if(checked){
                    accountType = "SipXCom"
                }
            }
            
            Keys.onReturnPressed: {
                sipComButton.checked = true
            }
        }
    }
}
