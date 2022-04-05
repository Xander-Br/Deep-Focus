import { Component, OnInit, ElementRef, ViewChild } from "@angular/core";
import { Student } from "./dto/Student";
import {ScoresResponse} from "./dto/ScoresResponse";
import { Element } from "@angular/compiler";
import elements = chrome.devtools.panels.elements;
import {
    Chart,
    CategoryScale,
    LineController,
    LineElement,
    PointElement,
    LinearScale,
    Title,
} from "chart.js";
import { interval, Subscription } from "rxjs";
import { MatSort, Sort } from "@angular/material/sort";
import { HttpClient } from "@angular/common/http";
import { MatTableDataSource } from "@angular/material/table";
import {Class} from "./dto/Class";

Chart.register(
    LineController,
    LineElement,
    PointElement,
    LinearScale,
    Title,
    CategoryScale
);

const refresh_time: number = 30000;

@Component({
    selector: "app-root",
    templateUrl: "./app.component.html",
    styleUrls: ["./app.component.css"],
})



export class AppComponent implements OnInit {
    streams: Element[] = [];
    displayed_columns: string[] = ["name", "score"];
    average_score = 0.8;
    student_list: Student[] = [];
    dataSource = new MatTableDataSource<Student>();
    classResponse: Class = new Class();

    refresh() {

    }

    lb_state: string = "Attentif";
    last_label: number = 0;

    // Test pour voir la mise en page
    constructor(private elementRef: ElementRef, private httpClient: HttpClient) {
        for (let i = 0; i < 40; i++) {

        }
    }

    ngOnInit() {
        this.chart_init();
        this.newRequest(refresh_time);
        this.getHistory();

    }

    getHistory(){
      this.httpClient.get<number[]>("http://localhost:5000/getHistory").subscribe(next =>
      {
        this.loadHistory(next);
      });

    }

    chart: any;
    chart_init() {
        const dataset = {
            labels: [],
            datasets: [
                {
                    label: "Class scores",
                    data: [],
                    borderColor: "rgb(75, 192, 192)",
                    tension: 0.3,
                },
            ],
        };

        this.chart = new Chart("canvas", {
            type: "line",
            data: dataset,
            options: {
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                    },
                },
            },
        });
    }

    url_get_score: string = 'http://localhost:5000/get_scores';
    score_list: any;

    newRequest(refresh_time: any) {
        // Obtention de la liste des scores
        this.httpClient.get<Class>(this.url_get_score)
            .subscribe(res => {
               this.classResponse = res;
               this.dataSource.data = this.classResponse.users;
            });

        // Pour mettre a jour la table
        this.dataSource.data = this.classResponse.users;


        this.lb_state = (this.classResponse.class_average > 0.8) ?  "Attentif : " : "Inattentif : ";
        this.lb_state += Math.floor(this.classResponse.class_average *100).toString() + "%";

        // Ajout d'un point sur la graphique
        this.addData(this.chart, this.classResponse.class_average * 100);

        setTimeout(() => {
            this.newRequest(refresh_time);
        }, refresh_time);
    }

    compute_score(score_list:  any) {
        let all_sum = 0;
        let score:number = 0;

        for (let key in score_list) {
            score = 0;
            for (let val in score_list[key].scores) {
                score += Number(val);
            }

            this.student_list = []
            this.student_list.push({
                name: key,
                //score: score,
                //score_list: score_list[key]
            });

            all_sum += score_list[key];
        }

        // Retourne la moyenne générale
        return all_sum/Object.keys(score_list).length;
    }


    loadHistory(history: number[]){
      for(let n in history){
        this.addData(this.chart, history[n] * 100);
      }
      this.average_score = history[history.length-1];
      this.lb_state = (this.average_score > 0.8) ?  "Attentif : " : "Inattentif : ";
      this.lb_state += Math.floor(this.average_score *100).toString() + "%";;
    }

    addData(chart: Chart, average_score: any) {
        this.last_label += 1;

        // @ts-ignore
        chart.data.labels.push(this.last_label.toString() + "m");
        chart.data.datasets.forEach((dataset: { data: any[]; }) => {
            dataset.data.push(average_score);
        });
        chart.update();
    }
}
