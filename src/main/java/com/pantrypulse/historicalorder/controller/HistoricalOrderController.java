package com.pantrypulse.historicalorder.controller;

import com.pantrypulse.historicalorder.dto.HistoricalOrderDto;
import com.pantrypulse.historicalorder.service.HistoricalOrderService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@Tag(
        name="Historical Order API",
        description="Manage historical order records.."
)

@RestController
@RequestMapping("/api/historical-orders")

public class HistoricalOrderController {

    private final HistoricalOrderService historicalOrderService;

    public HistoricalOrderController(HistoricalOrderService historicalOrderService) {
        this.historicalOrderService = historicalOrderService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public HistoricalOrderDto addHistoricalOrder(
            @Valid @RequestBody HistoricalOrderDto dto) {

        return historicalOrderService.addHistoricalOrder(dto);
    }
    @Operation(
    		summary="Get Historical Orders",
    		description="returns all historical orders."
    		)

    @GetMapping
    public List<HistoricalOrderDto> getAllHistoricalOrders() {
        return historicalOrderService.getAllHistoricalOrders();
    }
    @Operation(
    	    summary = "Get  Historical Orders by ID",
    	    description = "Returns a specific historical order ."
    	)
    @GetMapping("/{id}")
    public HistoricalOrderDto getHistoricalOrderById(
            @PathVariable Long id) {

        return historicalOrderService.getHistoricalOrderById(id);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteHistoricalOrder(@PathVariable Long id) {
        historicalOrderService.deleteHistoricalOrder(id);
    }

}