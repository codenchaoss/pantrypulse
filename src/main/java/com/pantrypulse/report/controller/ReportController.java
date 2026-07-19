package com.pantrypulse.report.controller;

import com.pantrypulse.report.dto.ReportSummaryDto;
import com.pantrypulse.report.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/summary")
    public ReportSummaryDto getSummary() {
        return reportService.getSummary();
    }
}