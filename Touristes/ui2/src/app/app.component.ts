import { Component } from '@angular/core';
import {Student} from "./dto/Student";
import {Element} from "@angular/compiler";
import elements = chrome.devtools.panels.elements;


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'ui2';

  studentList: Student[] = [];
  streams: Element[] = [];


  getAllStreams(){
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.executeScript(tabs[0].id!, {
        code: "document.getElementsByTagName('video');"
      })
    });
  }

  recieveAllStreams(resultArray: any){
    console.log(resultArray[0]);
  }


}



