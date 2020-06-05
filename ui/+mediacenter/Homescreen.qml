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

Image {
    anchors.fill: parent
    source: Qt.resolvedUrl("../images/bg.jpg")
    
    Component.onCompleted: {
        configButton.forceActiveFocus()
    }
    
    ColumnLayout {
        id: root
        anchors.fill: parent
        
        Item {
            height: Kirigami.Units.gridUnit * 5
        }
        
        ListModel {
            id: sampleModel
            ListElement {example: "Call X"}
            ListElement {example: "Call X and say Y"}
            ListElement {example: "Accept call"}
            ListElement {example: "Accept call and say Y"}
            ListElement {example: "Hang up"}
            ListElement {example: "List contacts"}
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.6)
            
            ColumnLayout {
                anchors.fill: parent
                
                RowLayout {
                    Layout.leftMargin: Kirigami.Units.largeSpacing
                    Layout.fillWidth: true
                    
                    Image {
                        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                        Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                        source: Qt.resolvedUrl("../images/icon.png")
                    }
                    
                    Kirigami.Heading {
                        level: 1
                        Layout.leftMargin: Kirigami.Units.largeSpacing
                        text: "VoIP" 
                    }
                }
                
                Kirigami.Heading {
                    level: 3
                    Layout.leftMargin: Kirigami.Units.largeSpacing
                    text: "VoIP with Baresip, make and take calls with Mycroft" 
                }
                
                Kirigami.Separator {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: hd2.contentHeight + Kirigami.Units.largeSpacing
                    color: Kirigami.Theme.linkColor
                    
                    Kirigami.Heading {
                        id: hd2
                        level: 3
                        width: parent.width
                        anchors.left: parent.left
                        anchors.leftMargin: Kirigami.Units.largeSpacing
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Some examples to get you started, try asking..."
                    }
                }
                                
                ListView {
                    id: skillExampleListView
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop
                    Layout.preferredHeight: contentItem.childrenRect.height
                    keyNavigationEnabled: false
                    clip: true
                    focus: false
                    highlightFollowsCurrentItem: false
                    snapMode: ListView.SnapToItem
                    model: sampleModel
                    KeyNavigation.down: configButton
                    delegate: Kirigami.BasicListItem {
                        id: rootCard
                        reserveSpaceForIcon: false
                        label: "Hey Mycroft, " + model.example
                    }
                }
                
                Button {
                    id: configButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: Kirigami.Units.gridUnit * 4
                    
                    background: Rectangle {
                        color: "#629ade"
                        radius: Kirigami.Units.gridUnit
                        border.width: configButton.activeFocus ? Kirigami.Units.largeSpacing : 0
                        border.color: configButton.activeFocus ? Kirigami.Theme.linkColor : "transparent"
                    }
                    
                    contentItem: Item {
                        Image {
                            anchors.centerIn: parent
                            width: Kirigami.Units.iconSizes.medium
                            height: width
                            source: "../images/configure.png"
                        }
                    }
                    
                    onClicked: {
                        voipLoaderView.setSource("Configure.qml")
                    }
                    
                    Keys.onReturnPressed: {
                        clicked()
                    }
                }
            }
        }
        
        Item {
            height: Kirigami.Units.gridUnit * 5
        }
    }
}
