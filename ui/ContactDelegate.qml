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

Kirigami.AbstractListItem {
    id: contactDelegate
    backgroundColor: Qt.rgba(0, 0, 0, 1)
    
    contentItem: Item {
        implicitWidth: delegateLayout.implicitWidth;
        implicitHeight: delegateLayout.implicitHeight;
        
        RowLayout {
            id: delegateLayout
            anchors {
                left: parent.left;
                top: parent.top;
                right: parent.right;
            }
            spacing: Math.round(Kirigami.Units.gridUnit / 2)

            Image {
                id: contactIcon
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                source: "images/avatar.png"
            }

            Kirigami.Heading {
                id: contactNameLabel
                level: 2
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                color: "white"
                elide: Text.ElideRight
                text: name
                textFormat: Text.PlainText
            }
            
            Label {
                id: contactUrlLabel
                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                color: "white"
                opacity: 0.8
                elide: Text.ElideRight
                text: url
                textFormat: Text.PlainText
            }
        }
    }
    
    onClicked: {
        triggerGuiEvent("voip.jarbas.callContact", {"contact": name})
    }
}
