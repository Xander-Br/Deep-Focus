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

Chart.register(
    LineController,
    LineElement,
    PointElement,
    LinearScale,
    Title,
    CategoryScale
);

@Component({
    selector: "app-root",
    templateUrl: "./app.component.html",
    styleUrls: ["./app.component.css"],
})
export class AppComponent implements OnInit {
    streams: Element[] = [];
    displayedColumns: string[] = ["name", "score"];
    averageScore = 81;
    studentList: Student[] = [];
    lb_state: string = "Attentif";
    last_label: number = 0;

    // Test pour voir la mise en page
    constructor(private elementRef: ElementRef, private httpClient: HttpClient) {
        for (let i = 0; i < 40; i++) {
            this.studentList.push({
                name: "alexandre",
                score: 0.9 - i * 0.02,
                score_list: []
            });
        }
    }

    ngOnInit() {
        this.chart_init();
        this.setDelay(this.refresh_delay, this.labels, this.datas);
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

    url_get_score: string = 'http://localhost:5000/get_score';
    score_list: any;

    refresh_delay: number = 10000;

    // TO MODIFY - delete two next
    labels: any = ["4", "5", "6", "7"];
    datas: any = [20, 50, 90, 85];
    setDelay(refresh_delay: any, labels: any, datas: any) {
        // TO MODIFY - 4 ligne a supprimé
        let label = labels.shift();
        let data = datas.shift();
        labels.push(label);
        datas.push(data);

        // Obtention de la liste des scores
        this.httpClient.get<ScoresResponse>(this.url_get_score)
            .subscribe(ScoreResponse => {
               this. score_list = ScoreResponse.scores_list;
            });

        // TO MODIFY - decomment et delete +2
        //let average_score = this.compute_score(this.score_list);
        let average_score = 0.9;

        this.lb_state = (average_score > 0.8) ?  "Attentif - " : "Inattentif - ";
        this.lb_state += (average_score*100).toString() + "%";

        this.addData(this.chart, data);

        setTimeout(() => {
            this.setDelay(refresh_delay, labels, datas);
        }, refresh_delay);
    }

    compute_score(score_list: any) {
        let all_sum = 0;
        let score = 0;
        for (let key in score_list) {
            score = 0;
            score_list[key].forEach((a: { value: number; }) => score += a.value);

            this.studentList.push({
                name: key,
                score: score,
                score_list: score_list[key]
            });

            all_sum += score_list[key];

        }
        return Object.keys(score_list).length;
    }

    addData(chart: Chart, average_score: any) {
        this.last_label += 1;

        // @ts-ignore
        chart.data.labels.push(this.last_label.toString() + "m");
        chart.data.datasets.forEach((dataset) => {
            dataset.data.push(average_score);
        });
        chart.update();
    }
}
