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
    id: failedView
            
    Rectangle {
        id: failBackground
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: -Kirigami.Units.largeSpacing
        height: parent.height
        color: "#33258f"
        clip: true
        
        Rectangle {
            id: notLoggedIn
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: Kirigami.Units.gridUnit * 2
            anchors.rightMargin: Kirigami.Units.gridUnit * 2
            height: Kirigami.Units.gridUnit * 5 + Kirigami.Units.largeSpacing
            color: Qt.rgba(0, 0, 0, 0.8)
            radius: Kirigami.Units.gridUnit
            
            Image {
                id: fImage
                anchors.top: parent.top
                anchors.topMargin: Kirigami.Units.largeSpacing + Kirigami.Units.smallSpacing
                anchors.horizontalCenter: parent.horizontalCenter
                width: Kirigami.Units.iconSizes.medium
                height: width
                source: "images/failed-connection.png" 
            }
            
            Kirigami.Heading {
                id: connectionTextHeading
                wrapMode: Text.WordWrap
                level: 1
                anchors.top: fImage.bottom
                anchors.topMargin: Kirigami.Units.largeSpacing * 2
                anchors.horizontalCenter: parent.horizontalCenter
                font.bold: true
                text: "Connection Failed"
                color: "white"
            }
        }
    }
}
 
 
 
