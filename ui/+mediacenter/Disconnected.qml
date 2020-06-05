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
    id: disconnectedView
            
    Rectangle {
        id: l1
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: -Kirigami.Units.largeSpacing
        height: parent.height / 2
        color: "#057cfc"
        clip: true
                        
        Rectangle {
            width: parent.width * 0.28
            height: width
            color: "transparent"
            border.width: 4
            border.color: Kirigami.Theme.backgroundColor
            radius: 1000
            clip: true
            anchors.centerIn: parent
        }
        
        Rectangle {
            width: parent.width * 0.35
            height: parent.height * 0.40
            color: "transparent"
            border.width: 4
            border.color: Kirigami.Theme.backgroundColor
            anchors.bottomMargin: -Kirigami.Units.gridUnit * 2
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            radius: Kirigami.Units.gridUnit * 2
            clip: true
        }
    }
        
    Item {
        id: bottomAreaA
        anchors.top: l1.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing

        Button {
            id: callDisconnected
            anchors.bottom: parent.bottom
            anchors.bottomMargin: Kirigami.Units.largeSpacing
            width: parent.width
            height: Kirigami.Units.gridUnit * 4
            
            background: Rectangle {
                color: Kirigami.Theme.backgroundColor
                radius: Kirigami.Units.gridUnit
            }
        
            contentItem: Item {
                Image {
                    anchors.right: connectionTextHeading.left
                    anchors.rightMargin: Kirigami.Units.largeSpacing + Kirigami.Units.smallSpacing
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.height * 0.75
                    height: width
                    source: "../images/disconnected.png" 
                }
                Label {
                    id: connectionTextHeading
                    wrapMode: Text.WordWrap
                    anchors.centerIn: parent
                    font.bold: true
                    text: "Call Disconnected"
                    color: Kirigami.Theme.textColor
                }
            }
        }
    }
}
 
 
 
