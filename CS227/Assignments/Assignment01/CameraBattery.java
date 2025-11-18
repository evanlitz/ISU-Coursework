package hw1;
/**
 * 
 * @author 
 * 
 * Evan Litzer 					2/9/2023			:)
 * 
 * Models a removable/rechargeable camera battery that can be charged by a wall charger (external) and a camera USB port. 
 * The battery can only be in one place at a time, as there are methods to remove or move the battery to another location.
 * Each type of charging has its own unique way of replenishing the battery.
 * 
 */
public class CameraBattery {
	/**
	 * Amount of available external charging settings.
	 */
	public static final int NUM_CHARGER_SETTINGS = 4 ;
	/**
	 * Rate at which the battery is charged used in both charging methods.
	 */
	public static final double CHARGE_RATE = 2.0 ;
	/**
	 * Default camera power consumption, or rate at which charge is expended by camera.
	 */
	public static final double DEFAULT_CAMERA_POWER_CONSUMPTION = 1.0 ;
	/**
	 * Amount of charge for the battery.
	 */
	private double batteryCharge ;
	/**
	 * Maximum amount of charge for the battery.
	 */
	private double batteryCapacity ;
	/**
	 * Maximum amount of charge capacity for the camera when charging the battery.
	 */
	private double cameraCapacity ;
	/**
	 * Amount of charge for the camera when battery is inserted.
	 */
	private double cameraCharge ;
	/**
	 * Total amount of drained battery charge expended across multiple drains.
	 */
	private double totalDrain ;
	/**
	 * External charger setting decided by the user through pushing button.
	 */
	private int chargerSetting ;
	/**
	 * Rate at which battery charge is used when connected to camera.
	 */
	private double cameraConsumption ;
	/**
	 * Maximum amount of battery charge for the external charger.
	 */
	private double externalCapacity ;
	/**
	 * Amount of charge for external charger when battery is connected.
	 */
	private double externalCharge ;
	
	
	
	/**
	 * 
	 * Constructs a new camera battery simulation. Battery begins disconnected from charger/camera. Starting battery charge and battery capacity is provided by user.
	 * If starting charge exceeds capacity, charge is set to capacity. External charge setting is set to 0.
	 * Total drain is reset to 0, as well as all capacities and charges of chargers.
	 * Camera consumption is set to the default camera power consumption variable.
	 * 
	 * @param batteryStartingCharge
	 * @param batteryMax
	 */
	public CameraBattery(double batteryStartingCharge, double batteryMax)
	{
		batteryCharge = batteryStartingCharge ;
		batteryCapacity = batteryMax ;
		batteryCharge = Math.min(batteryCharge, batteryCapacity) ;
		cameraCharge = 0 ;
		cameraCapacity = 0 ;
		totalDrain = 0 ;
		chargerSetting = 0 ;
		cameraConsumption = DEFAULT_CAMERA_POWER_CONSUMPTION ;
		externalCapacity = 0 ;
		externalCharge = 0 ;
		
	}
	
	/**
	 * Mutator method that simulates press of a button that increments external charger setting.
	 * If charger setting reaches 4, it is set back to 0 immediately.
	 */
	public void buttonPress()
	{
		chargerSetting += 1 ;
		chargerSetting = Math.max(0, chargerSetting % NUM_CHARGER_SETTINGS) ;
	}
	/**
	 * 
	 * Accessor method that simulates charging of camera battery if it is connected to the camera.
	 * Charge amount is decided by the inputted minutes and charge rate.
	 * Charging cannot exceed battery capacity and does not compute when the battery is disconnected.
	 * Returns amount of battery replenished during call.
	 * 
	 * @param minutes
	 * @return
	 */
	
	
	public double cameraCharge(double minutes)
	{
		double tempCharge = cameraCharge ;
		cameraCharge += (CHARGE_RATE * minutes) ;
		cameraCharge = Math.min(cameraCapacity, cameraCharge) ;
		batteryCharge += cameraCharge - tempCharge ;
		batteryCharge = Math.min(batteryCapacity, batteryCharge) ;
		return cameraCharge - tempCharge ;
	}
	
	
	
	
	/**
	 * 
	 * Accessor method that simulates the draining of charge of a camera battery if connected to the camera.
	 * Drain amount is determined through the inputted minutes amount and camera consumption constant.
	 * Draining cannot exceed amount of battery charge and does not drain any charge when battery is disconnected from camera.
	 * Returns amount of battery drained during call.
	 * @param minutes
	 * @return
	 */
	
	public double drain(double minutes)
	{
		double tempDrain = cameraCharge ;
		cameraCharge -= (minutes *  cameraConsumption) ;
		cameraCharge = Math.max(cameraCharge, 0) ;
		batteryCharge -= tempDrain - cameraCharge ;
		batteryCharge = Math.min(batteryCapacity, batteryCharge) ;
		totalDrain += (tempDrain - cameraCharge) ;
		return tempDrain - cameraCharge ;
	}
	
	/**
	 * 
	 * Accessor method that simulated the charging of a camera battery from an external wall charger.
	 * Amount of charge is determined through the inputted minutes, charge rate constant, and charger setting. 
	 * Charge cannot exceed the camera battery capacity and will not charge at all if battery is disconnected from wall charger.
	 * Returns amount of battery charged during call.
	 * 
	 * @param minutes
	 * @return
	 */
	public double externalCharge(double minutes)
	{
		double tempCharge = externalCharge ;
		externalCharge += (minutes * CHARGE_RATE * chargerSetting) ;
		externalCharge = Math.min(externalCapacity, externalCharge) ;
		batteryCharge += externalCharge - tempCharge ;
		batteryCharge = Math.min(batteryCapacity, batteryCharge) ;
		return externalCharge - tempCharge ;
	}
	
	
	/**
	 * Mutator method that resets the total amount of drained battery back to 0.
	 */
	
	public void resetBatteryMonitor()
	{
		totalDrain = 0 ;
	}
	
	/**
	 * Accessor method that returns the current capacity of the battery.
	 * @return
	 */

	public double getBatteryCapacity()
	{
		return batteryCapacity ;
	}
	/**
	 * Accessor method that returns the current amount of charge in the battery.
	 * @return
	 */
	
	public double getBatteryCharge()
	{
		return batteryCharge ;
	}
	
	/**
	 * Accessor method that returns the current charge of the camera.
	 * @return
	 */
	
	public double getCameraCharge()
	{
		return cameraCharge ;
	}
	
	/**
	 * Accessor method that returns the current camera consumption rate.
	 * @return
	 */
	
	public double getCameraPowerConsumption()
	{
		return cameraConsumption ;
	}
	
	/**
	 * Accessor method that returns the current external charger setting.
	 * @return
	 */
	
	public int getChargerSetting()
	{
		return chargerSetting ;
	}
	
	/**
	 * Accessor method that returns the total amount of drained battery charge.
	 * @return
	 */
	
	public double getTotalDrain()
	{
		return totalDrain ;
	}
	
	/**
	 * Mutator method that simulates battery being connected to external charger.
	 * Sets external capacity and charge to battery's ones.
	 * Sets camera capacity and charge to 0.
	 */
	
	public void moveBatteryExternal()
	{
		externalCapacity = batteryCapacity ;
		externalCharge = batteryCharge ;
		cameraCapacity = 0 ;
		cameraCharge = 0 ;
	}
		
	/**
	 * Mutator method that simulates the battery being connected to the camera.
	 * Sets camera charge and capacity to battery's. 
	 * Sets external charge and capacity to 0.
	 */
	
	public void moveBatteryCamera()
	{
		cameraCharge = batteryCharge ;
		cameraCapacity = batteryCapacity ;
		externalCapacity = 0 ;
		externalCharge = 0 ;
	}
	
	/**
	 * Simulates removal of the battery from all chargers.
	 * Sets camera and external charger capacity and charge to 0.
	 */
	
	public void removeBattery()
	{
		cameraCharge = 0 ;
		cameraCapacity = 0 ;
		externalCapacity = 0 ;
		externalCharge = 0 ;
	}
		
	/**
	 * Mutator method that allows user to change the camera power consumption to preferred amount.
	 * @param cameraPowerConsumption
	 */
	
	public void setCameraPowerConsumption(double cameraPowerConsumption)
	{
		cameraConsumption = cameraPowerConsumption ;
	}
			

}
