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
    id: contactsPage
    anchors.fill: parent
    
    RowLayout {
        id: contactsPageHeading
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        
        Image {
            id: backButton
            Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.preferredWidth: Kirigami.Units.iconSizes.medium
            Layout.preferredHeight: Kirigami.Units.iconSizes.medium
            source: "images/back.png"
            
            MouseArea {
                anchors.fill: parent
                onClicked: Mycroft.MycroftController.sendRequest("mycroft.mark2.reset_idle", {})
            }
        }
        
        Kirigami.Heading {
            level: 1
            Layout.fillWidth: true
            Layout.leftMargin: -Kirigami.Units.iconSizes.medium
            horizontalAlignment: Text.AlignHCenter
            font.bold: true
            text: "Contacts"
            color: "#03adfc"
        }
    }
        
    Kirigami.Separator {
        id: headerSept
        anchors.top: contactsPageHeading.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        width: parent.width
        height: 1
    }
                    
    ListView {
        id: contactsView
        anchors.top: headerSept.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.bottomMargin: Kirigami.Units.gridUnit
        model: voipLoaderView.contactListModel
        clip: true
        delegate: ContactDelegate{}
    }
}
