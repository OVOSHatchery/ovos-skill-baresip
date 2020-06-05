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
    id: configurePage
    anchors.fill: parent
    
    Component.onCompleted: {
        userNameFieldBox.forceActiveFocus()
    }
        
    Kirigami.Heading  {
        id: contactsPageHeading
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: Kirigami.Units.gridUnit * 3
        horizontalAlignment: Text.AlignHCenter
        font.bold: true
        text: "Configure"
        color: Kirigami.Theme.highlightColor
    }
        
    Kirigami.Separator {
        id: headerSept
        anchors.top: contactsPageHeading.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        width: parent.width
        height: 1
    }
    
    Kirigami.Heading {
        level: 2
        id: accDetails
        anchors.top: headerSept.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: Kirigami.Units.largeSpacing
        horizontalAlignment: Text.AlignHCenter
        font.bold: true
        text: "Account Details"
        color: Kirigami.Theme.highlightColor
    }
    
    ConfigTypeBox {
        id: accountTypeBox
        anchors.top: accDetails.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: Kirigami.Units.gridUnit * 3
        KeyNavigation.down: userNameFieldBox
    }
     
    Rectangle {
        id: userNameFieldBox
        anchors.top: accountTypeBox.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: Kirigami.Units.largeSpacing
        height: Kirigami.Units.gridUnit * 4
        color: "transparent"
        border.width: userNameFieldBox.activeFocus ? Kirigami.Units.largeSpacing : 0
        border.color: userNameFieldBox.activeFocus ? Kirigami.Theme.linkColor : "transparent"
        KeyNavigation.down: gateWayFieldBox
        KeyNavigation.up: genButton
        
        TextField {
            id: userNameField
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            placeholderText: "Enter Username: example_"
            
            Keys.onReturnPressed: {
                userNameFieldBox.forceActiveFocus()
            }
        }
        
        Keys.onReturnPressed: {
            userNameField.forceActiveFocus()
        }
    }
    
    Rectangle {
        id: gateWayFieldBox
        anchors.top: userNameFieldBox.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: Kirigami.Units.largeSpacing
        height: Kirigami.Units.gridUnit * 4
        color: "transparent"
        border.width: gateWayFieldBox.activeFocus ? Kirigami.Units.largeSpacing : 0
        border.color: gateWayFieldBox.activeFocus ? Kirigami.Theme.linkColor : "transparent"
        KeyNavigation.down: passwordFieldBox
        KeyNavigation.up: userNameFieldBox

        TextField {
            id: gateWayField
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            placeholderText: "Enter Gateway: sip2sip.info"
            
            Keys.onReturnPressed: {
                gateWayFieldBox.forceActiveFocus()
            }
        }
        
        Keys.onReturnPressed: {
            gateWayField.forceActiveFocus()
        }
    }
    
    Rectangle {
        id: passwordFieldBox
        anchors.top: gateWayFieldBox.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: Kirigami.Units.largeSpacing
        height: Kirigami.Units.gridUnit * 4
        color: "transparent"
        border.width: passwordFieldBox.activeFocus ? Kirigami.Units.largeSpacing : 0
        border.color: passwordFieldBox.activeFocus ? Kirigami.Theme.linkColor : "transparent"
        KeyNavigation.down: updateConfig
        KeyNavigation.up: gateWayFieldBox

        TextField {
            id: passwordField
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            placeholderText: "Enter Password: example123"
            echoMode: TextInput.PasswordEchoOnEdit
            
            Keys.onReturnPressed: {
                passwordFieldBox.forceActiveFocus()
            }
        }
        
        Keys.onReturnPressed: {
            passwordField.forceActiveFocus()
        }
    }
    
    ColumnLayout {
        id: configPageButtonsView
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
    
        Button {
            id: updateConfig
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 4
            KeyNavigation.down: backButton
            KeyNavigation.up: passwordFieldBox
            
            background: Rectangle {
                color: "#629ade"
                radius: Kirigami.Units.gridUnit
                border.width: updateConfig.activeFocus ? Kirigami.Units.largeSpacing : 0
                border.color: updateConfig.activeFocus ? Kirigami.Theme.linkColor : "transparent"
            }
            
            contentItem: Item {
                Image {
                    anchors.centerIn: parent
                    width: Kirigami.Units.iconSizes.medium
                    height: width
                    source: "../images/update-config.png"
                }
            }
            
            onClicked: {
                triggerGuiEvent("voip.jarbas.updateConfig", {"username": userNameField.text, "gateway": gateWayField.text, "password": passwordField.text, "type": accountTypeBox.accountType})
            }
            
            Keys.onReturnPressed: {
                clicked()
            }
        }
        
        Button {
            id: backButton
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 4
            KeyNavigation.up: updateConfig
            
            background: Rectangle {
                color: "#ff9d00"
                radius: Kirigami.Units.gridUnit
                border.width: backButton.activeFocus ? Kirigami.Units.largeSpacing : 0
                border.color: backButton.activeFocus ? Kirigami.Theme.linkColor : "transparent"
            }
            
            contentItem: Item {
                Image {
                    anchors.centerIn: parent
                    width: Kirigami.Units.iconSizes.medium
                    height: width
                    source: "../images/back.png"
                }
            }
            
            onClicked: {
                voipLoaderView.setSource("Homescreen.qml")
            }
            
            Keys.onReturnPressed: {
                clicked()
            }
        }
    }
}
 
